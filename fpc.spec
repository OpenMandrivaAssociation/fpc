# (cjw) to bootstrap fpc for a new architecture ARCH, run
# rpm -bb --define 'cross_target $ARCH' --target $ARCH fpc.spec

%define build_cross %{?cross_target:1}%{!?cross_target:0}
%define cross_prefix %{?cross_target:cross-%{cross_target}-}
%if %{build_cross}
%define fpc_target %{cross_target}
%else
%define fpc_target %_arch
%endif
%if "%{fpc_target}" == "ppc"
%define fpc_target powerpc
%endif
%if "%{fpc_target}" == "i686"
%define fpc_target i386
%endif
%if "%{fpc_target}" == "ppc64"
%define fpc_target powerpc64
%endif
%if "%{fpc_target}" == "ppc64le"
%define fpc_target powerpc64le
%endif
%define fpc_short_target %_target_cpu
%if "%{fpc_short_target}" == "x86_64"
%define fpc_short_target x64
%endif
%if "%{fpc_short_target}" == "znver1"
%define fpc_short_target x64
%endif
%if "%{fpc_short_target}" == "i686"
%define fpc_short_target 386
%endif
%if "%{fpc_short_target}" == "aarch64"
%define fpc_short_target a64
%endif
%if "%{fpc_short_target}" == "armv7hnl"
%define fpc_short_target arm
%endif
%if "%{fpc_short_target}" == "ppc64"
%define fpc_short_target powerpc64
%endif
%if "%{fpc_short_target}" == "ppc64le"
%define fpc_short_target powerpc64le
%endif

%define debug_package %{nil}

%define fpcversion %{version}
%define fpcdir %{_prefix}/lib/%{name}/%{fpcversion}
%define docdir %{_datadir}/doc/fpc-%{fpcversion}

%define builddocdir %{buildroot}%{docdir}
%define buildmandir %{buildroot}%{_datadir}
%define buildbindir %{buildroot}%{_bindir}
%define buildlibdir %{buildroot}%{_libdir}
%define buildexampledir %{builddocdir}/examples

Summary: 	Free Pascal Compiler
Name: 		fpc
Version: 	3.2.0
Release: 	3
License: 	GPLv2+ and LGPLv2+ with exceptions
Group: 		Development/Other
Url: 		http://www.freepascal.org/
Source0:	https://downloads.sourceforge.net/project/freepascal/Source/%{version}/fpc-%{version}.source.tar.gz
# Bootstrap compilers
Source10:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}-x86_64-linux.tar
Source11:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}.i386-linux.tar
Source12:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}.arm-linux.tar
Source13:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}.aarch64-linux.tar
Source14:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}.powerpc64-linux.tar
Source15:	http://downloads.sourceforge.net/project/freepascal/Linux/%{version}/fpc-%{version}.powerpc64le-linux.tar
Source20:	fpc.cft
Source100:	%{name}.rpmlintrc
Patch1:		fpc-use_bfd_linker.patch
Patch2:		fpc-3.2.0--fix-lib-paths-on-aarch64.patch
ExclusiveArch:	%{ix86} %{x86_64} %{arm} %{aarch64} %{ppc64} %{ppc64le}
Requires:	gcc
Requires:	fpc-base == %{version}
Requires:	fpc-units == %{version}
BuildRequires:  texlive-latex
BuildRequires:  texlive-epsf
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	pkgconfig(ncurses)
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
(FCL), gtk, ncurses, zlib, mysql, postgres, ibase bindings.

%package	src
# Needed for e.g. lazarus
Summary:	Source code of Free Pascal Compiler
Group:		Development/Other
BuildArch:	noarch

%description	src
The source code of Freepascal for documentation and code generation
purposes.

%package	base
Summary:	Ide and rtl units with some base unit
Group:		Development/Other

%description base
This package consists FPC IDE and only RTL units for using with classical 
CLI Pascal programm. It also includes:

- X11 (Xlib, Xutil)
- NCurses
- ZLib.

%package	units
Summary:	Units not included in fpc-base
Group:		Development/Other
Requires:	fpc-base == %{version}

%description	units
This package consists units not include in fpc-base packets. Use it if you
need all units instead RTL and X11,NCurses and ZLib only.

%prep
%setup -q -a 10 -a 11 -a 12 -a 13 -a 14 -a 15
%autopatch -p1
TOP="`pwd`"
cd fpc-%{version}?%{fpc_target}-%{_os}
./install.sh <<EOF
$TOP/bootstrap
n
n
n
n
n
EOF

cd "$TOP"
mkdir -p linker
ln -s %_bindir/ld.bfd linker/ld
ln -s %_bindir/ld.bfd linker/ld.bfd

%build
TOP="`pwd`"
export PATH="$TOP"/linker:"$TOP/bootstrap/bin:$PATH"
export PATH="$TOP/bootstrap/bin":$PATH
install -dm 755 fpc_src
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

STARTPP=ppc%{fpc_short_target}

make compiler_cycle ${EXTRA_FLAGS} FPC=${STARTPP}
#
make rtl_clean rtl_smart FPC=${NEWPP} ${EXTRA_FLAGS}
make packages_smart FPC=${NEWPP} ${EXTRA_FLAGS}
make utils_all FPC=${NEWPP} ${EXTRA_FLAGS}
#%if !%{build_cross}
#	make -C docs pdf FPDOC=${NEWFPDOC} FPC=${NEWPP} ${EXTRA_FLAGS}
#%endif

%install
#NEWPPUFILES=`pwd`/utils/ppufiles
%if %{build_cross}
EXTRA_FLAGS="CPU_TARGET=%{fpc_target} BINUTILSPREFIX=%{cross_target}-linux-"
NEWPP=`pwd`/compiler/ppcross%{fpc_short_target}
NEWFCPMAKE=/usr/bin/fpcmake
%else
EXTRA_FLAGS=
NEWPP=`pwd`/compiler/ppc%{fpc_short_target}
NEWFCPMAKE=`pwd`/utils/fpcm/bin/*/fpcmake
%endif
INSTALLOPTS="FPC=${NEWPP} INSTALL_PREFIX=%{buildroot}/%{_prefix} INSTALL_LIBDIR=%{buildlibdir} \
                INSTALL_DOCDIR=%{builddocdir} INSTALL_BINDIR=%{buildbindir} \
                INSTALL_BASEDIR=%{buildlibdir}/%{name}/%{version} \
                CODPATH=%{buildlibdir}/%{name}/lexyacc"
	make compiler_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make rtl_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make packages_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
	make utils_distinstall ${INSTALLOPTS} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}

%if %{build_cross}
	rm -rf %{buildexampledir}
%else
#	make demo_install ${INSTALLOPTS} INSTALL_SOURCEDIR=%{buildexampledir} FPCMAKE=${NEWFCPMAKE} ${EXTRA_FLAGS}
#	make doc_install ${INSTALLOPTS} INSTALL_DOCDIR=%{builddocdir} FPCMAKE=${NEWFCPMAKE}
#	mv %{buildroot}/%{_prefix}/doc/%{name}-%{version}/examples/* %{buildexampledir} 
#	make man_install ${INSTALLOPTS} INSTALL_PREFIX=%{buildmandir} FPCMAKE=${NEWFCPMAKE}
%endif

        # create link
	ln -sf %{fpcdir}/ppc%{fpc_short_target} %{buildroot}%{_bindir}/ppc%{fpc_short_target}
	
	#make fcl_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}
	#make api_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}
	#make packages_exampleinstall ${INSTALLOPTS} DOCINSTALLDIR=%{builddocdir}

install -dm 755 %{buildroot}%{_datadir}/fpcsrc
cp -a fpc_src/* %{buildroot}%{_datadir}/fpcsrc/

# fix permissions
find %{buildroot}%{_datadir}/fpcsrc/ -type d -exec chmod 755 {} \;
find %{buildroot}%{_datadir}/fpcsrc/ -type f -exec chmod 644 {} \;

%{buildroot}%{_bindir}/fpcmkcfg -p -t %{SOURCE20} -d "basepath=%{_exec_prefix}" -o %{buildroot}%{_sysconfdir}/fpc.cfg

# Workaround:
# newer rpm versions do not allow garbage
# delete lexyacc (The hardcoded library path is necessary because 'make
# install' places this file hardcoded at usr/lib)
rm -rf %{buildroot}/usr/lib/%{name}/lexyacc

%files

%files units
%{_libdir}/fpc/%{version}/units
%{_libdir}/fpc/%{version}/fpmkinst
# in fpc-base
%ifarch %{ix86}
%exclude %{_libdir}/fpc/%{version}/units/i386-linux/rtl
%exclude %{_libdir}/fpc/%{version}/units/i386-linux/x11
%exclude %{_libdir}/fpc/%{version}/units/i386-linux/ncurses
%exclude %{_libdir}/fpc/%{version}/units/i386-linux/zlib
%endif
%ifarch %{x86_64}
%exclude %{_libdir}/fpc/%{version}/units/x86_64-linux/rtl
%exclude %{_libdir}/fpc/%{version}/units/x86_64-linux/x11
%exclude %{_libdir}/fpc/%{version}/units/x86_64-linux/ncurses
%exclude %{_libdir}/fpc/%{version}/units/x86_64-linux/zlib
%endif
%ifarch %{aarch64}
%exclude %{_libdir}/fpc/%{version}/units/aarch64-linux/rtl
%exclude %{_libdir}/fpc/%{version}/units/aarch64-linux/x11
%exclude %{_libdir}/fpc/%{version}/units/aarch64-linux/ncurses
%exclude %{_libdir}/fpc/%{version}/units/aarch64-linux/zlib
%endif

%files src
%{_datadir}/fpcsrc

%files base
%doc %{_defaultdocdir}/%{name}-%{version}
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/%{name}.cfg
%{_libdir}/libpas2jslib.so
%{_libdir}/fpc/%{version}/msg
%{_libdir}/fpc/%{version}/samplecfg
%ifarch %{ix86}
%{_libdir}/fpc/%{version}/units/i386-linux/rtl
%{_libdir}/fpc/%{version}/units/i386-linux/x11
%{_libdir}/fpc/%{version}/units/i386-linux/ncurses
%{_libdir}/fpc/%{version}/units/i386-linux/zlib
%{_libdir}/fpc/%{version}/ppc386
%endif
%ifarch %{x86_64}
%{_libdir}/fpc/%{version}/units/x86_64-linux/rtl
%{_libdir}/fpc/%{version}/units/x86_64-linux/x11
%{_libdir}/fpc/%{version}/units/x86_64-linux/ncurses
%{_libdir}/fpc/%{version}/units/x86_64-linux/zlib
%{_libdir}/fpc/%{version}/ppcx64
%endif
%ifarch %{aarch64}
%{_libdir}/fpc/%{version}/units/aarch64-linux/rtl
%{_libdir}/fpc/%{version}/units/aarch64-linux/x11
%{_libdir}/fpc/%{version}/units/aarch64-linux/ncurses
%{_libdir}/fpc/%{version}/units/aarch64-linux/zlib
%{_libdir}/fpc/%{version}/ppca64
%endif

%ifarch %arm
%{_libdir}/fpc/%{version}/ppcarm
%endif
