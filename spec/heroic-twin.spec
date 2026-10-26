%global name heroic-twin
%global version 1.0.0
%global release 1
%global distroot /home/amd/Documents/AI_Output/heroic-fork/heroic/dist

Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        An Open Source Launcher for GOG, Epic Games and Amazon Games (offline-friendly fork)
License:        GPL-3.0-only
URL:            https://github.com/RiRiRawrZ615/HeroicGamesLauncher
Vendor:         Heroic Games Launcher <heroicgameslauncher@protonmail.com>
BuildArch:      x86_64
Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       (libXtst or libXtst6)
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       (libuuid or libuuid1)

%description
Offline-friendly fork of Heroic Games Launcher (upstream v2.22.4 base).
Adds a real Online/Offline Mode (Settings > General) that stops all
background online checks when offline, and fixes the startup hang before
GUI init on machines with no network. Fork modifications authored by
Qwen 3.8 for RiRiRawrZ615.
Fork home: https://github.com/RiRiRawrZ615/HeroicGamesLauncher

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/Heroic
cp -a %{distroot}/linux-unpacked/. %{buildroot}/opt/Heroic/

mkdir -p %{buildroot}/usr/bin
ln -sf /opt/Heroic/heroic-twin %{buildroot}/usr/bin/heroic-twin

mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/heroic-twin.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Heroic Games Launcher
Comment=An Open Source Launcher for GOG, Epic Games and Amazon Games
Exec=heroic-twin
Icon=heroic-twin
Categories=Game;
Terminal=false
EOF

mkdir -p %{buildroot}/usr/share/icons/hicolor
for s in 16x16 32x32 48x48 64x64 128x128 256x256 512x512; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/$s/apps
  cp %{distroot}/.icon-set/icon_${s}.png %{buildroot}/usr/share/icons/hicolor/$s/apps/heroic-twin.png
done
mkdir -p %{buildroot}/usr/share/icons/hicolor/1024x1024/apps
cp %{distroot}/.icon-set/icon_1024.png %{buildroot}/usr/share/icons/hicolor/1024x1024/apps/heroic-twin.png

%files
%dir /opt
/opt/Heroic/*
%attr(4755, root, root) /opt/Heroic/chrome-sandbox
/usr/bin/heroic-twin
/usr/share/applications/heroic-twin.desktop
/usr/share/icons/hicolor
