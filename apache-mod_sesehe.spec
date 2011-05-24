#Module-Specific definitions
%define mod_name mod_sesehe
%define mod_conf A55_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Modify or remove "Server: " HTTP response header
Name:		apache-%{mod_name}
Version:	0.1.0
Release:	%mkrel 10
Group:		System/Servers
License:	Apache License
URL:		http://jok.is-a-geek.net/mod_sesehe.php
Source0:	http://jok.is-a-geek.net/code/mod_sesehe.c
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The ServerTokens directive currently can at best be set to Prod, which will
cause apache to return "Apache" as Server header. Some problem still occurs:

First, the level of security by obscurity of this directive is not acceptable
by some people that just want to change it to some other value, without
re-compiling Apache, or people that even want to simply drop the "Server: "
header. Secondly, if apache is configured as a reverse proxy, and a malformed
request is received, then it will display its own server token instead of the
backend one, so we need to handle error response header.

I developed this tiny module by hijacking normal behavior of (reverse) proxy
feature of Apache : i.e. even if a request is not a proxy request, I tag it as
if it was, to make Apache core let me do what I want with this header.

%prep

%setup -q -c -T

cp %{SOURCE0} mod_sesehe.c
cp %{SOURCE1} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c mod_sesehe.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/mod_sesehe.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_sesehe.so
