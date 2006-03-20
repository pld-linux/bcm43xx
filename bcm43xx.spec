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
%define	_snap	060319
%define	_fwcutter_ver	003
%define	_rel	0.1
Release:	0.20%{_snap}.%{_rel}
Summary:	Broadcom BCM43xx series driver for Linux
Summary(pl):	Sterownik do kart Broadcom BCM43xx
Name:		bcm43xx
Version:	0.0.1
License:	GPL v2
Group:		Base/Kernel
Source0:	http://tara.shadowpimps.net/~bcm43xx/bcm43xx-snapshots/standalone/bcm43xx/bcm43xx-standalone-%{_snap}.tar.bz2
# Source0-md5:	fbc0215969a18ccf09f8dc07faf5dd6d
Source1:	http://download.berlios.de/bcm43xx/bcm43xx-fwcutter-%{_fwcutter_ver}.tar.bz2
# Source1-md5:	89b407d920811cfd15507da17f901bb0
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
%setup -q -n %{name}-standalone-%{_snap} -a1
%patch0 -p1
sed -i 's/KBUILD_MODNAME/"bcm43xx"/' \
	drivers/net/wireless/bcm43xx/*.[hc]
ln -s %{_includedir}/linux/softmac/net drivers/net/wireless/bcm43xx/
mv %{name}-fwcutter-%{_fwcutter_ver}/README README.fwcutter
cat > drivers/net/wireless/bcm43xx/Makefile << EOF
CFLAGS += -DCONFIG_BCM43XX=1
CFLAGS += -DCONFIG_BCM43XX_DMA=1
CFLAGS += -DCONFIG_BCM43XX_PIO=1
%{?debug:CFLAGS += -DCONFIG_BCM43XX_DEBUG=1}

obj-m += bcm43xx.o

bcm43xx-objs := bcm43xx_main.o bcm43xx_ilt.o \
	bcm43xx_radio.o bcm43xx_phy.o \
	bcm43xx_power.o bcm43xx_wx.o \
	bcm43xx_leds.o bcm43xx_ethtool.o \
	bcm43xx_xmit.o bcm43xx_sysfs.o \
	%{?debug:bcm43xx_debugfs.o} \
	bcm43xx_dma.o bcm43xx_pio.o
EOF

%build

%if %{with userspace}
%{__make} -C %{name}-fwcutter-%{_fwcutter_ver} \
	CFLAGS="%{rpmcflags} -std=c99 -Wall -pedantic -D_BSD_SOURCE"	\
	CC="%{__cc}"
%endif

%if %{with kernel}
cd drivers/net/wireless/bcm43xx/
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h

	%if %{with dist_kernel}
		%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	%else
		install -d o/include/config
		touch o/include/config/MARKER
		ln -sf %{_kernelsrcdir}/scripts o/scripts
	%endif
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv bcm43xx{,-$cfg}.ko
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}
install %{name}-fwcutter-%{_fwcutter_ver}/bcm43xx-fwcutter $RPM_BUILD_ROOT%{_bindir}
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/net
install drivers/net/wireless/bcm43xx/bcm43xx-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/bcm43xx.ko
%if %{with smp} && %{with dist_kernel}
install drivers/net/wireless/bcm43xx/bcm43xx-smp.ko \
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
%doc README README.fwcutter
%attr(755,root,root) %{_bindir}/bcm43xx-fwcutter
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
