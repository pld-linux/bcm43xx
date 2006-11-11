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
%define	_snap	060618
%define	_fwcutter_ver	005
%define	_rel	3
Summary:	Broadcom BCM43xx series driver for Linux
Summary(pl):	Sterownik do kart Broadcom BCM43xx
Name:		bcm43xx
Version:	0.0.1
Release:	0.20%{_snap}.%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	%{name}-standalone-%{_snap}.tar.bz2
# Source0-md5:	e82bb24ac2cc5557d1648f7bd7e016cf
Source1:	http://download.berlios.de/bcm43xx/%{name}-fwcutter-%{_fwcutter_ver}.tar.bz2
# Source1-md5:	af9d7ce9794b00f0ee73d3a6bfb321ac
Patch0:		%{name}-local_headers.patch
URL:		http://bcm43xx.berlios.de/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.326
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

%package -n kernel%{_alt_kernel}-net-bcm43xx
Summary:	Broadcom BCM43xx driver for Linux
Summary(pl):	Sterownik do karty Broadcom BCM43xx dla Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-net-bcm43xx
This package contains the Linux driver for the Broadcom BCM43xx
Ethernet network adapter.

%description -n kernel%{_alt_kernel}-net-bcm43xx -l pl
Pakiet zawiera sterownik dla Linuksa do kart sieciowych Broadcom
BCM43xx.

%package -n kernel%{_alt_kernel}-smp-net-bcm43xx
Summary:	Broadcom BCM43xx driver for Linux SMP
Summary(pl):	Sterownik do karty Broadcom BCM43xx dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-net-bcm43xx
This package contains the Linux SMP driver for the Broadcom BCM43xx
series Ethernet Network Adapter.

%description -n kernel%{_alt_kernel}-smp-net-bcm43xx -l pl
Pakiet zawiera sterownik dla Linuksa SMP do kart sieciowych Broadcom
BCM43xx.

%prep
%setup -q -n %{name}-standalone-%{_snap} -a1
%patch0 -p1
sed -i 's/KBUILD_MODNAME/"bcm43xx"/' \
	drivers/net/wireless/bcm43xx/*.[hc]
ln -s %{_includedir}/linux/softmac/net drivers/net/wireless/bcm43xx/
mv %{name}-fwcutter-%{_fwcutter_ver}/README README
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
%build_kernel_modules -m bcm43xx
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}
install %{name}-fwcutter-%{_fwcutter_ver}/bcm43xx-fwcutter $RPM_BUILD_ROOT%{_bindir}
%endif

%if %{with kernel}
cd drivers/net/wireless/bcm43xx/
%install_kernel_modules -m bcm43xx -d kernel/drivers/net
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-bcm43xx
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-bcm43xx
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-net-bcm43xx
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-net-bcm43xx
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/bcm43xx-fwcutter
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-bcm43xx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/bcm43xx.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-bcm43xx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/bcm43xx.ko*
%endif
%endif
