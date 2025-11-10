import { useEffect, useRef, useState } from 'react';
import { useCollab } from '../../context/CollabProviderContext';
import { ProblemPanel } from './ProblemPanel';
import { CodeEditor } from './CodeEditor';
import { TopBar } from './TopBar';
import type { WebrtcProvider } from 'y-webrtc';

interface CollabSessionProps {
  userId: string;
  problem: ProblemData | null;
  partnerName: string;
  isReconnecting: boolean;
  handleExit: () => void;
  minutes: string;
  seconds: string;
}

interface ProblemData {
  title: string;
  description: string;
  code_template: string;
  category: string;
  difficulty: string;
}

export function CollabSession({
  userId,
  problem,
  partnerName,
  isReconnecting,
  handleExit,
  minutes,
  seconds,
}: CollabSessionProps) {
  // Add audio context for voice chat
  const { provider } = useCollab();
  const [isMuted, setIsMuted] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const localStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  // const addedAudioEls = useRef<HTMLAudioElement[]>([]);

  useEffect(() => {
    if (!provider) return;
    const room = (
      provider as WebrtcProvider & {
        room?: { webrtcConns?: Map<string, { peer: RTCPeerConnection }> };
      }
    ).room;
    if (!room) {
      console.warn('⚠️ provider.room not available yet');
      return;
    }

    const cleanup: (() => void)[] = [];

    console.log('🎙️ Initializing voice chat for room:');

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        console.log('🎧 Got local microphone stream', stream);
        localStreamRef.current = stream;
        stream.getTracks().forEach((t) => (t.enabled = false)); // start muted

        const attachToPeers = () => {
          const conns =
            room.webrtcConns ?? new Map<string, { peer: RTCPeerConnection }>();
          console.log('📡 Current peer connections:', [...conns.keys()]);

          conns.forEach((conn, peerId) => {
            const pc = conn.peer;
            if (!pc) {
              console.warn(`⚠️ Peer ${peerId} has no RTCPeerConnection yet`);
              return;
            }

            console.log(`🧩 Attaching audio track to peer ${peerId}`);

            // Try to ensure transceiver exists
            try {
              const trans = pc.addTransceiver('audio', {
                direction: 'sendrecv',
              });
              console.log(
                `🎛️ Added transceiver for ${peerId}`,
                trans?.direction
              );
            } catch (err) {
              console.warn(`⚠️ addTransceiver failed for ${peerId}:`, err);
            }

            // Temporarily enable tracks for negotiation
            stream.getTracks().forEach((t) => (t.enabled = true));

            // Add local audio tracks
            stream.getTracks().forEach((track) => {
              try {
                const sender = pc.addTrack(track, stream);
                console.log(
                  `🎧 Added track "${track.kind}" → peer ${peerId}`,
                  sender
                );
              } catch (e) {
                console.warn(`❌ addTrack failed for ${peerId}:`, e);
              }
            });

            // Mute again after short delay (so SDP includes audio)
            setTimeout(() => {
              stream.getTracks().forEach((t) => (t.enabled = false));
              console.log(
                `🔇 Disabled local audio track after negotiation for ${peerId}`
              );
            }, 2000);

            pc.ontrack = (event: RTCTrackEvent) => {
              console.log(
                `🎵 Received remote ${event.track.kind} from ${peerId}`
              );
              if (event.track.kind === 'audio') {
                const audio = document.createElement('audio');
                audio.autoplay = true;
                audio.srcObject = event.streams[0];
                document.body.appendChild(audio);
                cleanup.push(() => audio.remove());
              }
            };

            pc.onconnectionstatechange = () =>
              console.log(`🔗 ${peerId} connectionState:`, pc.connectionState);
            pc.oniceconnectionstatechange = () =>
              console.log(`❄️ ${peerId} ICE:`, pc.iceConnectionState);
            // pc.onicecandidate = (e) => {
            //   if (!e.candidate) {
            //     console.log(
            //       `📜 [${peerId}] Final local SDP:`,
            //       pc.localDescription?.sdp
            //     );
            //   }
            // };
          });
        };

        // Wait for peers
        const tryAttach = () => {
          const conns = room.webrtcConns;
          if (!conns || conns.size === 0) {
            console.log('⏳ No peers yet — retrying in 1s...');
            setTimeout(tryAttach, 1000);
          } else {
            console.log('✅ Found peers:', [...conns.keys()]);
            attachToPeers();
          }
        };
        tryAttach();

        // React to new peers joining
        provider.on(
          'peers',
          ({ added, removed }: { added: string[]; removed: string[] }) => {
            if (added?.length) console.log('🆕 Peers added:', added);
            if (removed?.length) console.log('❌ Peers removed:', removed);
            setTimeout(attachToPeers, 500);
          }
        );

        // Voice activity detection
        const audioCtx = new AudioContext();
        const analyser = audioCtx.createAnalyser();
        const src = audioCtx.createMediaStreamSource(stream);
        src.connect(analyser);
        analyser.fftSize = 512;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        audioCtxRef.current = audioCtx;
        analyserRef.current = analyser;

        const detectSpeech = () => {
          analyser.getByteFrequencyData(dataArray);
          const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
          setIsSpeaking(avg > 20 && !isMuted);
          requestAnimationFrame(detectSpeech);
        };
        detectSpeech();
      })
      .catch((err) => {
        console.error('🚨 Error accessing microphone:', err);
      });

    return () => {
      cleanup.forEach((fn) => fn());
      localStreamRef.current?.getTracks().forEach((t) => t.stop());
      audioCtxRef.current?.close();
    };
  }, [provider]);

  // // Voice setup: attach audio streams to peers from y-webrtc
  // useEffect(() => {
  //   if (!provider) return;
  //   console.log('Setting up voice streams with provider:', provider);

  //   // Get internal map of peer connections
  //   const internalProvider = provider as any;

  //   // Capture local microphone
  //   navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
  //     console.log('Got local audio stream:', stream);
  //     localStreamRef.current = stream;
  //     stream.getTracks().forEach((t) => (t.enabled = false));

  //     // Attach tracks to existing peers
  //     Object.values(internalProvider.webrtcConns || {}).forEach((conn: any) => {
  //       if (conn?.peer && conn.peer.signalingState !== 'closed') {
  //         stream
  //           .getTracks()
  //           .forEach((track) => conn.peer.addTrack(track, stream));
  //       }
  //     });

  //     // When new peers are added, attach audio to them
  //     provider.on('peers', ({ added }) => {
  //       added.forEach((peerId: string) => {
  //         const conn = internalProvider.webrtcConns?.[peerId];
  //         if (conn?.peer) {
  //           stream
  //             .getTracks()
  //                 .forEach((track) => conn.peer.addTrack(track, stream));
  //             console.log('Added local audio track to new peer:', peerId);

  //           // Handle incoming audio tracks from that peer
  //           conn.peer.ontrack = (event: RTCTrackEvent) => {
  //             if (event.track.kind === 'audio') {
  //               const audioEl = document.createElement('audio');
  //               audioEl.autoplay = true;
  //               audioEl.srcObject = event.streams[0];
  //               document.body.appendChild(audioEl);
  //                 addedAudioEls.current.push(audioEl);
  //                 console.log('audio track event:', event.streams[0]);
  //             }
  //           };
  //         }
  //       });
  //       console.log('Current peers:', internalProvider.webrtcConns);
  //     });

  //     // Voice activity detection (analyser)
  //     const audioCtx = new AudioContext();
  //     const analyser = audioCtx.createAnalyser();
  //     const source = audioCtx.createMediaStreamSource(stream);
  //     source.connect(analyser);
  //     analyser.fftSize = 512;
  //     const dataArray = new Uint8Array(analyser.frequencyBinCount);

  //     audioCtxRef.current = audioCtx;
  //     analyserRef.current = analyser;

  //     const detectSpeech = () => {
  //       analyser.getByteFrequencyData(dataArray);
  //       const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
  //       setIsSpeaking(avg > 20 && !isMuted);
  //       requestAnimationFrame(detectSpeech);
  //     };
  //     detectSpeech();
  //   });

  //   return () => {
  //     addedAudioEls.current.forEach((el) => el.remove());
  //     localStreamRef.current?.getTracks().forEach((t) => t.stop());
  //     audioCtxRef.current?.close();
  //   };
  // }, [provider]);

  const handleToggleMute = () => {
    if (!localStreamRef.current) return;
    const mute = !isMuted;
    localStreamRef.current.getTracks().forEach((t) => (t.enabled = !mute));
    setIsMuted(mute);
  };

  return (
    <div className="min-h-screen flex flex-col px-20 py-10">
      <TopBar
        onExit={handleExit}
        category={problem ? problem.category : ''}
        difficulty={problem ? problem.difficulty : ''}
        minutes={minutes}
        seconds={seconds}
        partnerName={partnerName}
        isMuted={isMuted}
        isSpeaking={isSpeaking}
        onToggleMute={handleToggleMute}
      />

      {isReconnecting && (
        <div className="bg-yellow-100 text-yellow-800 text-center p-2 rounded mb-4 animate-pulse">
          ⚠️ Connection lost — attempting to reconnect...
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 justify-center overflow-hidden">
        <div className="card shadow-sm border-1 border-base-200 p-10 overflow-y-auto">
          <ProblemPanel
            title={problem ? problem.title : ''}
            description={problem ? problem.description : ''}
          />
        </div>

        <div className="col-span-2 card shadow-sm border-1 border-base-200 p-10">
          <div className="w-full overflow-visible">
            <CodeEditor
              userId={userId}
              defaultCode={problem ? problem.code_template : ''}
              isReconnecting={isReconnecting}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
