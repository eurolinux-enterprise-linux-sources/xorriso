Summary:         ISO-9660 and Rock Ridge image manipulation tool
Name:            xorriso
Version:         1.4.8
Release:         3%{?dist}
License:         GPLv3+
Group:           Applications/Archiving
URL:             http://scdbackup.sourceforge.net/xorriso_eng.html
# Source0:         https://www.gnu.org/software/%{name}/%{name}-%{version}.tar.gz
Source0:         %{name}-%{version}-clean.tar.gz
Source1:         https://www.gnu.org/software/%{name}/%{name}-%{version}.tar.gz.sig
Source2:         gpgkey-44BC9FD0D688EB007C4DD029E9CBDFC0ABC0A854.gpg
Source3:         xorriso_servicemenu.desktop
Patch0:          xorriso-no-libjte.patch
BuildRequires:   gnupg2
BuildRequires:   gcc, gcc-c++, readline-devel, libacl-devel, zlib-devel
BuildRequires:   autoconf, automake, libtool
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires(post):  /sbin/install-info
Requires(preun): /sbin/install-info
%endif
Requires:        kde-filesystem >= 4
Requires(post):  %{_sbindir}/alternatives, coreutils
Requires(preun): %{_sbindir}/alternatives

%description
Xorriso is a program which copies file objects from POSIX compliant
filesystems into Rock Ridge enhanced ISO-9660 filesystems and allows
session-wise manipulation of such filesystems. It can load management
information of existing ISO images and it writes the session results
to optical media or to filesystem objects. Vice versa xorriso is able
to copy file objects out of ISO-9660 filesystems.

Filesystem manipulation capabilities surpass those of mkisofs. Xorriso
is especially suitable for backups, because of its high fidelity of
file attribute recording and its incremental update sessions. Optical
supported media: CD-R, CD-RW, DVD-R, DVD-RW, DVD+R, DVD+R DL, DVD+RW,
DVD-RAM, BD-R and BD-RE. 

%prep
# Verify GPG signatures
#gpghome="$(mktemp -qd)" # Ensure we don't use any existing gpg keyrings
#gpgv2 --homedir "$gpghome" --keyring %%{SOURCE2} %%{SOURCE1} %%{SOURCE0}
#rm -rf "$gpghome" # Cleanup tmp gpg home dir

%setup -q
%patch0 -p1

aclocal -I .
autoconf
automake --foreign --add-missing --copy --include-deps

%build
%configure --disable-libjte
%make_build
#doxygen doc/doxygen.conf

%install
%make_install

# Don't install any libtool .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}.la

# Clean up for later usage in documentation
rm -rf $RPM_BUILD_ROOT%{_defaultdocdir}

# Install the KDE service menu handler
install -D -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/kde4/services/ServiceMenus/xorriso_servicemenu.desktop

# Symlink xorriso as mkisofs (like in cdrkit)
ln -sf xorriso $RPM_BUILD_ROOT%{_bindir}/mkisofs

# Some file cleanups
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

# Don't ship proof of concept for the moment
rm -f $RPM_BUILD_ROOT{%{_bindir},%{_infodir},%{_mandir}/man1}/xorriso-tcltk*

%check
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$RPM_BUILD_ROOT%{_libdir}"
cd releng
./run_all_auto -x ../xorriso/xorriso || (cat releng_generated_data/log.*; exit 1)

%post
%if 0%{?rhel} && 0%{?rhel} <= 7
/sbin/install-info %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
/sbin/install-info %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :
%endif

link=`readlink %{_bindir}/mkisofs`
if [ "$link" == "xorriso" ]; then
  rm -f %{_bindir}/mkisofs
fi

%{_sbindir}/alternatives --install %{_bindir}/mkisofs mkisofs %{_bindir}/xorriso 40 \
  --slave %{_mandir}/man1/mkisofs.1.gz mkisofs-mkisofsman %{_mandir}/man1/xorrisofs.1.gz

%preun
if [ $1 = 0 ]; then
%if 0%{?rhel} && 0%{?rhel} <= 7
  /sbin/install-info --delete %{_infodir}/xorrecord.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorriso.info.gz %{_infodir}/dir || :
  /sbin/install-info --delete %{_infodir}/xorrisofs.info.gz %{_infodir}/dir || :
%endif

  %{_sbindir}/alternatives --remove mkisofs %{_bindir}/xorriso
fi

%files
%license COPYING
%doc AUTHORS COPYRIGHT README ChangeLog
%ghost %{_bindir}/mkisofs
%{_bindir}/osirrox
%{_bindir}/xorrecord
%{_bindir}/xorriso
%{_bindir}/xorrisofs
%{_mandir}/man1/xorrecord.1*
%{_mandir}/man1/xorriso.1*
%{_mandir}/man1/xorrisofs.1*
%{_infodir}/xorrecord.info*
%{_infodir}/xorriso.info*
%{_infodir}/xorrisofs.info*
%{_datadir}/kde4/services/ServiceMenus/xorriso_servicemenu.desktop

%changelog
* Tue Mar 26 2019 Pavel Cahyna <pcahyna@redhat.com> - 1.4.8-3
- Disable libjte to make the build more similar to the libisofs builds
- Remove unneeded files from sources

* Fri Mar 15 2019 Pavel Cahyna <pcahyna@redhat.com> - 1.4.8-2
- Merge relevant Fedora/EPEL changes up to 1.5.0-2, but keep the 1.4.8 version

* Tue Mar 12 2019 Pavel Cahyna <pcahyna@redhat.com> 1.4.8-1
- Initial release, based on libisoburn from Fedora
