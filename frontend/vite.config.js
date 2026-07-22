import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

function copyCargoShipPlugin() {
  const src = 'C:\\Users\\playe\\OneDrive\\Desktop\\DOO IT\\padava-processor\\frontend\\public\\cargo ship.jpg';
  const dest = path.resolve(__dirname, 'public/cargo-ship.jpg');

  const doCopy = () => {
    try {
      const publicDir = path.resolve(__dirname, 'public');
      if (!fs.existsSync(publicDir)) {
        fs.mkdirSync(publicDir, { recursive: true });
      }
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, dest);
        console.log('[Vite] Successfully copied cargo ship.jpg to public/cargo-ship.jpg');
      }
    } catch (err) {
      console.error('[Vite] Copy error:', err);
    }
  };

  return {
    name: 'copy-cargo-ship',
    buildStart: doCopy,
    configureServer(server) {
      doCopy();
    }
  };
}

export default defineConfig({
  plugins: [react(), copyCargoShipPlugin()],
  server: {
    port: 3000,
    open: true,
    fs: {
      allow: ['..', 'C:/Users/playe']
    }
  },
});
