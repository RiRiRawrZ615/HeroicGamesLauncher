/**
 * @file  Sets the runtime Electron app name.
 *
 * The fork keeps a different *package* name (`heroic-twin`) so it is a
 * distinct npm/electron-builder package, but it intentionally uses the same
 * runtime app name as upstream Heroic (`heroic`) so that
 * `app.getPath('userData')` resolves to the exact same folder the original
 * uses. This means the fork shares all of the original's data files
 * (config.json, the electron-store files, wine/tools caches, game configs,
 * wine prefixes and install paths) and is fully compatible with it.
 *
 * This module must be imported before any module that calls `app.getPath`,
 * so it is imported first in the main entrypoint.
 */
import { app } from 'electron'

// Keep the original app name so userData/store paths coincide with upstream.
app.name = 'heroic'

export const forkAppName = app.name
