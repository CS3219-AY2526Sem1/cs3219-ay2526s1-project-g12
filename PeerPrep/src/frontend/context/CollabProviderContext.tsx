import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import * as Y from 'yjs';
import { WebrtcProvider } from 'y-webrtc';

type CollabContextType = {
  ydoc: Y.Doc | null;
  provider: WebrtcProvider | null;
  roomId: string;
};

const CollabContext = createContext<CollabContextType>({
  ydoc: null,
  provider: null,
  roomId: '',
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

  useEffect(() => {
    const ydoc = new Y.Doc();
    console.log('Y.Doc created for room:', roomId);
    const provider = new WebrtcProvider(`room-${roomId}`, ydoc, {
      signaling: [import.meta.env.VITE_SIGNALING_SERVER_URL],
      peerOpts: {
        config: {
          iceServers: [{ urls: [import.meta.env.VITE_ICE_SERVERS] }],
        },
      },
    });
    console.log('WebRTC Provider:', provider);
    console.log('WebRTC ydoc:', ydoc);

    ydocRef.current = ydoc;
    providerRef.current = provider;
    setProviderReady(true);

    return () => {
      provider.destroy();
      ydoc.destroy();
    };
  }, [roomId]);

  if (!providerReady) return null;

  return (
    <CollabContext.Provider
      value={{
        ydoc: ydocRef.current,
        provider: providerRef.current,
        roomId,
      }}
    >
      {children}
    </CollabContext.Provider>
  );
}
