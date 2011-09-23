# (cjw) to bootstrap fpc for a new architecture ARCH, run
# rpm -bb --define 'cross_target $ARCH' --target $ARCH fpc.spec

%define useprebuiltcompiler 1

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

%define debug_package %{nil}

%define name fpc
%define version 2.4.4
%define release %mkrel 3
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
License: 	GPLv2+ and LGPLv2+ with exceptions
Group: 		Development/Other
Source:		http://surfnet.dl.sourceforge.net/sourceforge/freepascal/%{name}-%{version}.source.tar.gz
# This is only needed when useprebuiltcompiler is defined.
# But it's not in an 'if defined' block, since the file has to be included in the srpm
# Thus you should enable this line when useprebuildcompiler is defined for any target
Source1:	http://www.cnoc.nl/fpc/%{name}-%{version}.compiler.bin.tar.gz
Summary: 	Free Pascal Compiler
URL: 		http://www.freepascal.org/
BuildRoot: 	%{_tmppath}/%{name}-root
Requires:	gcc
Requires:	fpc-base == %{version}
Requires:	fpc-units == %{version}
%if ! %{defined useprebuiltcompiler}
BuildRequires:	fpc
%endif
BuildRequires: 	tetex-latex mysql-devel postgresql-devel ncurses-devel
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

%package src
# Needed for e.g. lazarus
Summary:	Source code of Free Pascal Compiler
Group:		Development/Other

%description src
The source code of Freepascal for documentation and code generation
purposes.

%package base
Summary:	Ide and rtl units with some base unit. May be useful for education with standart Pascal CLI programm
Group:		Development/Other

%description base
This package consists FPC IDE and only RTL units for using with classical CLI Pascal programm.
Also it consists:

- X11 (Xlib, Xutil)
- NCurses
- ZLib.

%package units
Summary:	Units not included in fpc-base
Group:		Development/Other
Requires: fpc-base == %{version}

%description units
This package consists units not include in fpc-base packets. Using it, if you need all units instead RTL and X11,NCurses and ZLib only.

%prep
%if %{defined useprebuiltcompiler}
%setup -a1 -n %{name}-%{version} -q
%else
%setup -n %{name}-%{version} -q
%endif

%build
mkdir -p fpc_src
cp -a rtl packages fpc_src
rm -rf fpc_src/packages/extra/amunits
rm -rf fpc_src/packages/extra/winunits

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

%if %{defined useprebuiltcompiler}
STARTPP=`pwd`/startcompiler/ppc%{fpc_short_target}
%else
STARTPP=ppc%{fpc_short_target}
%endif

	make compiler_cycle ${EXTRA_FLAGS} FPC=${STARTPP}
#
	make rtl_clean rtl_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make packages_smart FPC=${NEWPP} ${EXTRA_FLAGS}
	make ide_all FPC=${NEWPP} ${EXTRA_FLAGS}
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
	make ide_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
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

mkdir -p %{buildroot}%{_datadir}/fpcsrc
cp -a fpc_src/* %{buildroot}%{_datadir}/fpcsrc/

%clean
#	make compiler_clean
#	make rtl_clean
#	make fcl_clean
#	make api_clean
#	make packages_clean
#	make utils_clean

rm -rf $RPM_BUILD_ROOT
	
%post base
# Create config
%{fpcdir}/samplecfg %{fpcdir}

%files
%defattr(-,root,root)

%files units
%defattr(-,root,root)
%{_prefix}/lib/fpc/%{version}/units
# in fpc-base
%ifarch i586
%exclude %{_prefix}/lib/fpc/%{version}/units/i386-linux/rtl
%exclude %{_prefix}/lib/fpc/%{version}/units/i386-linux/x11
%exclude %{_prefix}/lib/fpc/%{version}/units/i386-linux/ncurses
%exclude %{_prefix}/lib/fpc/%{version}/units/i386-linux/zlib
%else
%exclude %{_prefix}/lib/fpc/%{version}/units/x86_64-linux/rtl
%exclude %{_prefix}/lib/fpc/%{version}/units/x86_64-linux/x11
%exclude %{_prefix}/lib/fpc/%{version}/units/x86_64-linux/ncurses
%exclude %{_prefix}/lib/fpc/%{version}/units/x86_64-linux/zlib
%endif

%files src
%defattr(-,root,root,-)
%{_datadir}/fpcsrc

%files base
%defattr(-,root,root,-)
%doc %{_defaultdocdir}/%{name}-%{version}
%{_bindir}/*
%{_prefix}/lib/fpc/lexyacc
%{_prefix}/lib/fpc/%{version}/ide
%{_prefix}/lib/fpc/%{version}/msg
%{_prefix}/lib/fpc/%{version}/samplecfg
%ifarch i586
%{_prefix}/lib/fpc/%{version}/units/i386-linux/rtl
%{_prefix}/lib/fpc/%{version}/units/i386-linux/x11
%{_prefix}/lib/fpc/%{version}/units/i386-linux/ncurses
%{_prefix}/lib/fpc/%{version}/units/i386-linux/zlib
%{_prefix}/lib/fpc/%{version}/ppc386
%else
%{_prefix}/lib/fpc/%{version}/units/x86_64-linux/rtl
%{_prefix}/lib/fpc/%{version}/units/x86_64-linux/x11
%{_prefix}/lib/fpc/%{version}/units/x86_64-linux/ncurses
%{_prefix}/lib/fpc/%{version}/units/x86_64-linux/zlib
%{_prefix}/lib/fpc/%{version}/ppcx64
%endif
