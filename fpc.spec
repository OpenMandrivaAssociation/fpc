# (cjw) to bootstrap fpc for a new architecture ARCH, run
# rpm -bb --define 'cross_target $ARCH' --target $ARCH fpc.spec

%define build_cross %{?cross_target:1}%{!?cross_target:0}
%define cross_prefix %{?cross_target:cross-%{cross_target}-}
%if %{build_cross}
%define fpc_target %{cross_target}
%else
%define fpc_target %_arch
%endif
%if %{fpc_target} == ppc
%define fpc_target powerpc
%endif
%define fpc_short_target %_target_cpu
%if %{fpc_short_target} == x86_64
%define fpc_short_target x64
%endif
%if %{fpc_short_target} == i586
%define fpc_short_target 386
%endif

%define name fpc
%define version 2.1.1
%define release %mkrel 0.4
%define fpcversion %{version}
%define fpcdir %{_prefix}/lib/%{name}/%{fpcversion}
%define docdir %{_datadir}/doc/fpc-%{fpcversion}

%define builddocdir %{buildroot}%{docdir}
%define buildmandir %{buildroot}%{_datadir}
%define buildbindir %{buildroot}%{_bindir}
%define buildlibdir %{buildroot}%{_libdir}
%define buildexampledir %{builddocdir}/examples


Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
ExclusiveArch: 	%{ix86} ppc x86_64
License: 	GPL
Group: 		Development/Other
Source: 	ftp://ftp.de.freepascal.org/pub/fpc/dist/source-%{version}/%{name}-%{version}.source.tar.bz2
Patch0:		fpc-makefile.patch
Summary: 	Free Pascal Compiler
URL: 		http://www.freepascal.org/
BuildRoot: 	%{_tmppath}/%{name}-root
Requires:	gcc
# Sad but true :(
BuildRequires:  fpc
BuildRequires: 	tetex-latex mysql-devel postgresql-devel
%if %{build_cross}
BuildRequires:	cross-%{cross_target}-binutils
%endif

%description	
The Free Pascal Compiler is a Turbo Pascal 7.0 and Delphi compatible 32bit
Pascal Compiler. It comes with fully TP 7.0 compatible run-time library.
Some extensions are added to the language, like function overloading. Shared
libraries can be linked. Basic Delphi support is already implemented (classes,
exceptions,ansistrings,RTTI). This package contains commandline compiler and
utils. Provided units are the runtime library (RTL), free component library
(FCL), gtk,ncurses,zlib, mysql,postgres,ibase bindings.

%prep
%setup -q -n %{name}

#%patch0

%build
%if %{build_cross}
fpcmake -T%{fpc_target}-linux
%endif

%if %{build_cross}
EXTRA_FLAGS="CPU_TARGET=%{fpc_target} BINUTILSPREFIX=%{cross_target}-linux-"
NEWPP=`pwd`/compiler/ppcross%{fpc_short_target}
%else
EXTRA_FLAGS=
NEWPP=`pwd`/compiler/ppc%{fpc_short_target}
%endif
NEWFPDOC=`pwd`/utils/fpdoc/fpdoc
	make compiler_cycle ${EXTRA_FLAGS}
	make rtl_clean rtl_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make packages_base_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make fcl_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make packages_extra_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make utils_all FPC=${NEWPP} ${EXTRA_FLAGS}
#%if !%{build_cross}
#	make -C docs pdf FPDOC=${NEWFPDOC} FPC=${NEWPP} ${EXTRA_FLAGS}
#%endif

%install
rm -Rf %{buildroot}
#NEWPPUFILES=`pwd`/utils/ppufiles
%if %{build_cross}
EXTRA_FLAGS="CPU_TARGET=%{fpc_target} BINUTILSPREFIX=%{cross_target}-linux-"
NEWPP=`pwd`/compiler/ppcross%{fpc_short_target}
NEWFCPMAKE=/usr/bin/fpcmake
%else
EXTRA_FLAGS=
NEWPP=`pwd`/compiler/ppc%{fpc_short_target}
NEWFCPMAKE=`pwd`//utils/fpcm/fpcmake
%endif
INSTALLOPTS="FPC=${NEWPP} INSTALL_PREFIX=%{buildroot}/%{_prefix} INSTALL_LIBDIR=%{buildlibdir} \
                INSTALL_DOCDIR=%{builddocdir} INSTALL_BINDIR=%{buildbindir}"
	make compiler_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make rtl_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make packages_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make fcl_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make utils_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}

%if %{build_cross}
	rm -rf %{buildexampledir}
%else
#	make demo_install ${INSTALLOPTS} INSTALL_SOURCEDIR=%{buildexampledir} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
#	make doc_install ${INSTALLOPTS} INSTALL_DOCDIR=%{builddocdir} FPCMAKE=${NEWFCPMAKE}
	#mv %{buildroot}/%{_prefix}/doc/%{name}-%{version}/examples/* %{buildexampledir} 
#	make man_install ${INSTALLOPTS} INSTALL_PREFIX=%{buildmandir} FPCMAKE=${NEWFCPMAKE}
%endif

        # create link
	ln -sf %{fpcdir}/ppc%{fpc_short_target} %{buildroot}%{_bindir}/ppc%{fpc_short_target}
	
	#make fcl_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}
	#make api_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}
	#make packages_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}


%clean
#	make compiler_clean
#	make rtl_clean
#	make fcl_clean
#	make api_clean
#	make packages_clean
#	make utils_clean

rm -rf $RPM_BUILD_ROOT
	
%post
# Create config
%{fpcdir}/samplecfg %{fpcdir}

%files
%defattr(-,root,root)
%doc utils/fpdoc/{COPYING,README}
%{_bindir}/*
%{_prefix}/lib/fpc
#%if !%{build_cross}
#%{_mandir}/*/*
#%endif

