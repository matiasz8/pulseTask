// Preload script - runs in isolated context
const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  app: {
    name: 'PulseTask',
    version: '0.2.0',
  },
});
