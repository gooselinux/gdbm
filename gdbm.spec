Summary: A GNU set of database routines which use extensible hashing
Name: gdbm
Version: 1.8.0
Release: 36%{?dist}
Source: http://ftp.gnu.org/gnu/gdbm/gdbm-%{version}.tar.gz
# Prevent gdbm from storing uninitialized memory content
# to database files.
# The change allows Valgrind users to debug their packages without
# dealing with gdbm-related noise. It also improves security, as 
# the uninitialized memory might contain sensitive informations 
# from other applications. The patch is taken from Debian.
# See rhbz#4457. (rhbz#572601)
# See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=208927
Patch0: gdbm-1.8.0-zeroheaders.patch
# Make gdbm buildable.
Patch1: gdbm-1.8.0-fhs.patch
# This patch was merged into gdbm-1.8.3.
Patch3: gdbm-1.8.0-64offset.patch
# Memory leak in gdbm_reorganize(gdb) (rhbz#572598)
# Fixed in gdbm-1.8.3
Patch4: gdbm-1.8.0-memleak.patch
# Make gdbm handle read(2) returning less data than it was asked for.
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=274417 (rhbz#572900)
Patch5: gdbm-1.8.0-shortread.patch
License: GPLv2+
URL: http://www.gnu.org/software/gdbm/
Group: System Environment/Libraries
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: libtool

%description
Gdbm is a GNU database indexing library, including routines which use
extensible hashing.  Gdbm works in a similar way to standard UNIX dbm
routines.  Gdbm is useful for developers who write C applications and
need access to a simple and efficient database or who are building C
applications which will use such a database.

If you're a C developer and your programs need access to simple
database routines, you should install gdbm.  You'll also need to
install gdbm-devel.

%package devel
Summary: Development libraries and header files for the gdbm library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires(post): info
Requires(preun): info

%description devel
Gdbm-devel contains the development libraries and header files for
gdbm, the GNU database system.  These libraries and header files are
necessary if you plan to do development using the gdbm database.

Install gdbm-devel if you are developing C programs which will use the
gdbm database library.  You'll also need to install the gdbm package.

%prep
%setup -q
%patch0 -p1 -b .zeroheaders
%patch1 -p1 -b .fhs
%patch3 -p1 -b .offset
%patch4 -p1 -b .memleak
%patch5 -p1 -b .shortread

# refresh config.sub, the original one does not recognize "redhat"
# as vendorname:
for f in /usr/share/automake-1.1?/config.sub; do
  :
done
cp -p $f .
libtoolize --force --copy
aclocal
autoconf

%build
%configure --disable-static

# flock does not work on nfs
# fcntl should be used instead of it
# see `man 2 flock`
# rhbz#477300
echo "/* We use fcntl locking (POSIX) instead of flock (BSD) */" >> autoconf.h
echo "#undef HAVE_FLOCK" >> autoconf.h

make

%install
rm -rf ${RPM_BUILD_ROOT}

%makeinstall install-compat

ln -sf gdbm/gdbm.h $RPM_BUILD_ROOT/%{_includedir}/gdbm.h
ln -sf libgdbm.so.2.0.0 $RPM_BUILD_ROOT/%{_libdir}/libgdbm.so

rm -f $RPM_BUILD_ROOT/%{_libdir}/libgdbm.la

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel
/sbin/install-info %{_infodir}/gdbm.info.gz %{_infodir}/dir \
      --entry="* gdbm: (gdbm).                   The GNU Database." || :

%preun devel
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/gdbm.info.gz %{_infodir}/dir \
      --entry="* gdbm: (gdbm).                   The GNU Database." || :
fi

%files
%defattr(-,root,root,-)
%doc COPYING NEWS README
%{_libdir}/libgdbm.so.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/libgdbm.so
%{_includedir}/gdbm*
%{_infodir}/*.info*
%{_mandir}/man3/*

%clean
rm -rf ${RPM_BUILD_ROOT}

%changelog
* Fri May 28 2010 Karel Klic <kklic@redhat.com> - 1.8.0-36
- Apply -shortread patch
  Resolves: #596163

* Mon Apr 12 2010 Karel Klic <kklic@redhat.com> - 1.8.0-35
- Use fcntl instead of flock for locking to make NFS safe
  Resolves: #581524

* Thu Mar 11 2010 Karel Klic <kklic@redhat.com> - 1.8.0-34
- -jbj patch replaced with -zeroheaders, which extends the header zeroing
  and also zeroes the buckets (#572601)
- Fixed a memory leak in gdbm_reorganize(gdb) (rhbz#572598)
- Handle read() returning less data than it was asked for (rhbz#572900)
- Remove static builds from the devel package (#556050)
- Moved autotools reinitialization from %%build to %%prep section

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.8.0-33.1
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.0-33
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Apr 17 2009 Stepan Kasal <skasal@redhat.com> - 1.8.0-32
- Clean up the spec, for merge review.

* Fri Feb 27 2009 Stepan Kasal <skasal@redhat.com> - 1.8.0-31
- drop *-cflags.patch, move all makefile fixes to *-fhs.patch
- propagate libdir to Makefile; no need to set it on cmdline

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.0-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jul 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.8.0-29
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.8.0-28
- Autorebuild for GCC 4.3

* Tue Apr 3 2007 Ondrej Dvoracek <odvorace@redhat.com> - 1.8.0-27
- made install-info use in scriptlets safe (#223688)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.8.0-26.2.1
- rebuild

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.8.0-26.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.8.0-26.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 24 2006 Warren Togami <wtogami@redhat.com> 1.8.0-26
- remove .la (#171535)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sat Apr 09 2005 Florian La Roche <laroche@redhat.com>
- rebuild

* Sun Aug  8 2004 Alan Cox <alan@redhat.com> 1.8.0-24
- Close bug #125319

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Oct  4 2002 Nalin Dahyabhai <nalin@redhat.com> 1.8.0-19
- rebuild

* Fri Sep 13 2002 Nalin Dahyabhai <nalin@redhat.com> 1.8.0-18.1
- run make with libdir overridden so that it has the value passed to configure
  instead of $(prefix)/lib

* Wed Jul 24 2002 Trond Eivind Glomsrød <teg@redhat.com> 1.8.0-18
- Remove cflags for large database support - not compatible 
  with databases without it

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Apr 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 1.8.0-15
- Use 64bit offset
- Patch to make the above not break from downsj@downsj.com (#63980) 

* Tue Feb 26 2002 Trond Eivind Glomsrød <teg@redhat.com> 1.8.0-14
- Rebuild

* Fri Jan 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 1.8.0-13
- Update location
- auto* changes to make it build

* Wed Oct 17 2001 Trond Eivind Glomsrød <teg@redhat.com> 1.8.0-11
- Add URL (# 54607)

* Mon Jun 25 2001 Nalin Dahyabhai <nalin@redhat.com>
- s/Copyright:/License:/g
- include text docs in binary package

* Tue Jun 12 2001 Than Ngo <than@redhat.com>
- fix to build against new libtool

* Mon Mar 19 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Make it respect RPM_OPT_FLAGS/CFLAGS - #32242. 
  Patch from dan@D00M.cmc.msu.ru

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun  5 2000 Jeff Johnson <jbj@redhat.com>
- FHS packaging.

* Mon Feb  7 2000 Bill Nottingham <notting@redhat.com>
- handle compressed manpages

* Tue Aug 10 1999 Jeff Johnson <jbj@redhat.com>
- make sure created database header is initialized (#4457).

* Tue Jun  1 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.8.0.
- repackage to include /usr/include/gdbm/*dbm.h compatibility includes.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 19)

* Thu Dec 17 1998 Cristian Gafton <gafton@redhat.com>
- build against glibc 2.1

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Thu Apr 30 1998 Cristian Gafton <gafton@redhat.com>
- gdbm-devel moved to Development/Libraries

* Wed Apr 08 1998 Cristian Gafton <gafton@redhat.com>
- buildroot and built for Manhattan

* Tue Oct 14 1997 Donnie Barnes <djb@redhat.com>
- spec file cleanups

* Thu Jun 12 1997 Erik Troan <ewt@redhat.com>
- built against glibc
