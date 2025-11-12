import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import * as Y from 'yjs';
import { WebrtcProvider } from 'y-webrtc';
import { VoiceConnectionManager } from './VoiceConnectionManager';

type CollabContextType = {
  ydoc: Y.Doc | null;
  provider: WebrtcProvider | null;
  roomId: string;
  voiceManager: VoiceConnectionManager | null;
};

const CollabContext = createContext<CollabContextType>({
  ydoc: null,
  provider: null,
  roomId: '',
  voiceManager: null,
});

export const useCollab = () => useContext(CollabContext);

type CollabProviderProps = {
  roomId: string;
  children: React.ReactNode;
};

export function CollabProvider({ roomId, children }: CollabProviderProps) {
  const [providerReady, setProviderReady] = useState(false);
  const ydocRef = useRef<Y.Doc | null>(null);
  const providerRef = useRef<WebrtcProvider | null>(null);
  const voiceManagerRef = useRef<VoiceConnectionManager | null>(null);

  useEffect(() => {
    let manager: VoiceConnectionManager;
    let ydoc: Y.Doc;
    let provider: WebrtcProvider;

    async function init() {
      try {
        // --- Collaborative Yjs provider ---
        ydoc = new Y.Doc();
        provider = new WebrtcProvider(`room-${roomId}`, ydoc, {
          signaling: [import.meta.env.VITE_SIGNALING_SERVER_URL],
          peerOpts: {
            config: {
              iceServers: [{ urls: [import.meta.env.VITE_ICE_SERVERS] }],
            },
          },
        });
        ydocRef.current = ydoc;
        providerRef.current = provider;
        setProviderReady(true);

        // --- Voice layer ---
        manager = new VoiceConnectionManager(
          import.meta.env.VITE_SIGNALING_SERVER_URL,
          roomId
        );
        await manager.initLocalMic(); // get mic tracks
        await manager.startCall(); // send offer
        voiceManagerRef.current = manager;
      } catch (err) {
        console.error('🚨 Error initializing CollabProvider:', err);
      }
    }

    init();

    return () => {
      provider.destroy();
      ydoc.destroy();
      manager.cleanup();
    };
  }, [roomId]);

  if (!providerReady) return null;

  return (
    <CollabContext.Provider
      value={{
        ydoc: ydocRef.current,
        provider: providerRef.current,
        roomId,
        voiceManager: voiceManagerRef.current,
      }}
    >
      {children}
    </CollabContext.Provider>
  );
}
