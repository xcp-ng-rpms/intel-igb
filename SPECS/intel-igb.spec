%define vendor_name Intel
%define vendor_label intel
%define driver_name igb
%define vf_param max_vfs
%define vf_maxvfs 7

%if %undefined module_dir
%define module_dir updates
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}
Version: 5.3.5.20
Release: 1%{?dist}
License: GPL

Source0: https://code.citrite.net/rest/archive/latest/projects/XS/repos/driver-intel-igb/archive?at=5.3.5.20&format=tar.gz&prefix=driver-intel-igb-5.3.5.20#/intel-igb.tar.gz


Provides: gitsha(https://code.citrite.net/rest/archive/latest/projects/XS/repos/driver-intel-igb/archive?at=5.3.5.20&format=tar.gz&prefix=driver-intel-igb-5.3.5.20#/intel-igb.tar.gz) = 8875494a986ffff5f1927dd132b0b6f9e15aca8f


BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n driver-%{name}-%{version}

%build
%{?cov_wrap} %{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
echo '# VFs-param: %{vf_param}' > %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo '# VFs-maxvfs-by-default: %{vf_maxvfs}' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo '# VFs-maxvfs-by-user:' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
echo 'options %{driver_name} %{vf_param}=0' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
%{?cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

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

%changelog
