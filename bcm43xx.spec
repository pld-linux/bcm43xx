#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%ifarch sparc
%undefine	with_smp
%endif
#
Summary:	Broadcom BCM43xx series driver for Linux
Summary(pl):	Sterownik do kart Broadcom BCM43xx
Name:		bcm43xx
Version:	0.0.1
%define	_snap	20060120
%define		_rel	0.1
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://ftp.berlios.de/pub/bcm43xx/snapshots/bcm43xx/%{name}-%{_snap}.tar.bz2
# Source0-md5:	4294c8a1f8c9c0f3ea71c8262d016cad
Patch0:		%{name}-local_headers.patch
URL:		http://bcm43xx.berlios.de/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
BuildRequires:	softmac-devel
%endif
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains the Linux driver for the Broadcom BCM43xx
Ethernet network adapter.

%description -l pl
Pakiet zawiera sterownik dla Linuksa do kart sieciowych Broadcom
BCM43xx.

%package -n kernel-net-bcm43xx
Summary:	Broadcom BCM43xx driver for Linux
Summary(pl):	Sterownik do karty Broadcom BCM43xx dla Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-net-bcm43xx
This package contains the Linux driver for the Broadcom BCM43xx
Ethernet network adapter.

%description -n kernel-net-bcm43xx -l pl
Pakiet zawiera sterownik dla Linuksa do kart sieciowych Broadcom
BCM43xx.

%package -n kernel-smp-net-bcm43xx
Summary:	Broadcom BCM43xx driver for Linux SMP
Summary(pl):	Sterownik do karty Broadcom BCM43xx dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-net-bcm43xx
This package contains the Linux SMP driver for the Broadcom BCM43xx
series Ethernet Network Adapter.

%description -n kernel-smp-net-bcm43xx -l pl
Pakiet zawiera sterownik dla Linuksa SMP do kart sieciowych Broadcom
BCM43xx.

%prep
%setup -q -n %{name}-%{_snap}
%patch0 -p1
cp -rf %{_usr}/src/softmac-include/net .

%build

%if %{with kernel}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
%ifarch ppc ppc64
	install -d include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-powerpc ] || ln -sf %{_kernelsrcdir}/include/asm-powerpc/* include/asm
	[ ! -d %{_kernelsrcdir}/include/asm-%{_target_base_arch} ] || ln -snf %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
%else
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%endif

	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}

	mv bcm43xx{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/net
install bcm43xx-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/bcm43xx.ko
%if %{with smp} && %{with dist_kernel}
install bcm43xx-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/bcm43xx.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-bcm43xx
%depmod %{_kernel_ver}

%postun	-n kernel-net-bcm43xx
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-bcm43xx
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-bcm43xx
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%endif

%if %{with kernel}
%files -n kernel-net-bcm43xx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/bcm43xx.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-bcm43xx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/bcm43xx.ko*
%endif
%endif
