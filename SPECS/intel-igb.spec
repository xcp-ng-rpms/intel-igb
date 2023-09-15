%global package_speccommit 1c40a02055bde96499f2ae25149cfc0662b55e31
%global usver 5.13.20
%global xsver 2
%global xsrel %{xsver}%{?xscount}%{?xshash}
%global package_srccommit 5.13.20
%define vendor_name Intel
%define vendor_label intel
%define driver_name igb
%define vf_param max_vfs
%define vf_maxvfs 7

%if %undefined module_dir
%define module_dir updates
%endif

## kernel_version will be set during build because then kernel-devel
## package installs an RPM macro which sets it. This check keeps
## rpmlint happy.
%if %undefined kernel_version
%define kernel_version dummy
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}
Version: 5.13.20
Release: %{?xsrel}%{?dist}
License: GPL
Source0: intel-igb.tar.gz
Patch0: igb-WoL-update.patch

BuildRequires: gcc
BuildRequires: kernel-devel
%{?_cov_buildrequires}
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n %{name}-%{version}
%{?_cov_prepare}

%build
cd src
KSRC=/lib/modules/%{kernel_version}/build OUT=kcompat_generated_defs.h CONFFILE=/lib/modules/%{kernel_version}/build/.config bash kcompat-generator.sh
cd ..
%{?_cov_wrap} %{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
echo '# VFs-param: %{vf_param}' > %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo '# VFs-maxvfs-by-default: %{vf_maxvfs}' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo '# VFs-maxvfs-by-user:' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo 'options %{driver_name} %{vf_param}=0' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
%{?_cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%{?_cov_install}

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
/lib/modules/%{kernel_version}/*/*.ko

%{?_cov_results_package}

%changelog
* Wed Aug 02 2023 Stephen Cheng <stephen.cheng@citrix.com> - 5.13.20-2
- CA-380604: Fix WoL defaults for I350 to be compatible with old OEM igb and upstream

* Tue Jul 18 2023 Stephen Cheng <stephen.cheng@citrix.com> - 5.13.20-1
- CP-42529: Update to version 5.13.20

* Mon Feb 14 2022 Ross Lagerwall <ross.lagerwall@citrix.com> - 5.3.5.20-3
- CP-38416: Enable static analysis

* Wed Dec 02 2020 Ross Lagerwall <ross.lagerwall@citrix.com> - 5.3.5.20-2
- CP-35517: Fix the build for koji
