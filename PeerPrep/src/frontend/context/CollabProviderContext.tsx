import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import * as Y from "yjs";
import { WebrtcProvider } from "y-webrtc";

type CollabContextType = {
  ydoc: Y.Doc | null;
  provider: WebrtcProvider | null;
  roomId: string;
};

const CollabContext = createContext<CollabContextType>({
  ydoc: null,
  provider: null,
  roomId: "",
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
    const provider = new WebrtcProvider(`room-${roomId}`, ydoc, {
      signaling: ["ws://localhost:4444"],
      peerOpts: {
        config: {
          iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }],
        },
      },
    });

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
