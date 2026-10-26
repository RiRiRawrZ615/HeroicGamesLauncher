# Heroic (offline fork)

An offline-friendly fork of [HeroicGamesLauncher](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher) (upstream v2.22.4, GPL-3.0).

The goal: stop the launcher from constantly phoning home to GitHub / winetricks
when there is no internet, and give you an explicit **Online/Offline Mode**.

## Package identity

| Field | Original | This fork |
|-------|----------|-----------|
| npm `name` | `heroic` | `heroic-twin` |
| electron-builder `appId` | `com.heroicgameslauncher.hgl` | `com.heroictwin.hgl` |
| Runtime app name (`app.name`) | `heroic` | `heroic` (forced) |
| Window title / productName | `Heroic Games Launcher` | `Heroic Games Launcher` |

The runtime app name is intentionally kept as `heroic` (see
`src/backend/constants/app_name.ts`, imported first in `main.ts`) so that
`app.getPath('userData')` resolves to the same folder the original uses.
Both launchers therefore **share the same data files**
(`~/.config/heroic/...`): `config.json`, the electron-store files, wine/tools
caches, game configs, wine prefixes and install paths. They are fully
compatible with each other.

## New feature: Online/Offline Mode

Settings > General > **Online/Offline Mode** (config key `networkMode`).

- **Auto (follow connection)** (default): online checks run only when the
  launcher detects it is online; nothing calls out when offline.
- **Online (always check for updates)**: always attempt online checks.
- **Offline (never check for updates)**: never call out, use locally cached
  release data.

What "online checks" cover (all suppressed in offline mode, and in auto mode
while offline):

- Electron `autoUpdater` self-update check on startup
- Heroic version / changelog banner (`getLatestReleases` / `getCurrentChangelog`)
- Wine/Proton release-list refresh (falls back to the local cache)
- Winetricks script download
- DXVK / VKD3D / dxmt tool updates
- Default wine auto-download

The mode is stored in the same `config.json` as every other setting. When it
changes, the backend pushes `networkMode-changed` to the frontend; a new IPC
`getForkMode` returns the current mode. The top "Offline" banner shows
"Offline Mode (manual)" while in offline mode.

## Bug fix: startup hang before the GUI initializes (no network / no adapter)

There was an upstream bug where, if there was no network connection (or no
present adapter), the application would hang before all of the GUI could
initialize.

Root cause (traced with instrumentation): the entire frontend tree is wrapped
in a `<Suspense>` boundary, and every component (including the `<Loading/>`
fallback itself) calls `useTranslation()` with react-i18next's `useSuspense:
true`. That only releases once i18next finishes loading the active language's
translations through the `i18next-http-backend`. In a "adapter present but no
usable route" state that async load can stall, so i18next never fires
`loaded`, the Suspense boundary never releases, and the whole UI stays frozen
before it finishes initializing.

Fixes applied (all offline-safe):
1. **Preload the active language** (and its resolved base form + the English
   fallback) into i18next's resource store *before* first render. i18next
   short-circuits its load when the resource bundle already exists, so the
   Suspense boundary releases immediately and first paint no longer depends on
   the network at all. Verified: the offline packaged build reaches
   "Frontend Ready" in the same second as startup and makes **zero** i18n
   backend fetches.
2. **Window-show safety net**: the main window is created `show: false` and is
   shown on `did-finish-load` (Wayland) / `ready-to-show`. A 5s timeout
   fallback now guarantees the window is shown even if that event never fires,
   and the show handler is idempotent.
3. **Offline mode stops the pinging loop**: when the mode is `offline`, the
   connectivity monitor no longer keeps re-pinging external endpoints (it
   reports `offline` directly), so nothing calls out and the banner is
   stable. Switching modes re-evaluates connectivity correctly.

## Files changed

New:
- `src/backend/network_mode.ts`
- `src/backend/constants/app_name.ts`
- `src/frontend/screens/Settings/components/OnlineMode.tsx`

Modified (wiring + guards):
- `package.json`, `electron-builder.yml` (identity)
- `src/common/types.ts`, `src/common/types/ipc.ts`
- `src/backend/config.ts`, `src/backend/main.ts`, `src/backend/online_monitor.ts`
- `src/backend/wine/manager/utils.ts`, `src/backend/tools/index.ts`
- `src/preload/api/misc.ts`
- `src/frontend/index.tsx` (i18n preload, so first paint is offline-safe)
- `src/frontend/state/GlobalState.tsx`, `src/frontend/state/ContextProvider.tsx`
- `src/frontend/types.ts`
- `src/frontend/components/UI/OfflineMessage/index.tsx`
- `src/frontend/screens/Settings/components/index.ts`
- `src/frontend/screens/Settings/sections/GeneralSettings/index.tsx`
- `public/locales/en/translation.json`

## Building

```bash
pnpm install
pnpm run build            # electron-vite build (main + preload + renderer)
pnpm exec electron-builder --linux AppImage rpm
```

Output: `dist/Heroic-1.0.0-linux-x86_64.AppImage` and `dist/Heroic-1.0.0-linux-x86_64.rpm`.

If `electron-builder` cannot build the RPM itself (its bundled fpm/Ruby is
incompatible with some distros, e.g. missing libcrypt.so.1), build it with the
system toolchain instead. After the AppImage step above, `dist/linux-unpacked`
and `dist/.icon-set` already exist, so:

```bash
rpmbuild -bb spec/heroic-twin.spec
# or point the spec at a different dist directory:
rpmbuild --define 'distroot /path/to/dist' -bb spec/heroic-twin.spec
```

Output: `~/rpmbuild/RPMS/x86_64/heroic-twin-1.0.0-1.x86_64.rpm` (installs to
`/opt/Heroic`, binary `heroic-twin`, desktop entry + icon set, same runtime
data dir as the official launcher).

Verified: `tsc --noEmit` clean, `electron-vite build` clean, all 177 jest
tests pass, AppImage builds and runs, and it resolves to `~/.config/heroic`
(shared with the original). The offline startup-hang fix was verified by
running the packaged build with no network (network namespace): it reaches
"Frontend Ready" in the same second as startup and makes zero i18n backend
fetches.
(shared with the original).
