import { useEffect, useRef, useState } from 'react';
import { useCollab } from '../../context/CollabProviderContext';
import { ProblemPanel } from './ProblemPanel';
import { CodeEditor } from './CodeEditor';
import { TopBar } from './TopBar';

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
  const { voiceManager } = useCollab();
  const [isMuted, setIsMuted] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (!voiceManager) return;

    const stream = voiceManager.getLocalStream();
    if (!stream) {
      console.warn('[UI] No local stream yet; speaking meter idle');
      return;
    }

    stream.getTracks().forEach((t) => (t.enabled = false)); // start muted
    const audioCtx = new AudioContext();
    const analyser = audioCtx.createAnalyser();
    const src = audioCtx.createMediaStreamSource(stream);
    src.connect(analyser);
    analyser.fftSize = 512;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const detectSpeech = () => {
      analyser.getByteFrequencyData(dataArray);
      const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setIsSpeaking(avg > 20 && !isMuted);
      requestAnimationFrame(detectSpeech);
    };
    detectSpeech();

    analyserRef.current = analyser;
    audioCtxRef.current = audioCtx;
    return () => {
      audioCtx.close();
    };
  }, [voiceManager]);

  const handleToggleMute = () => {
    if (!voiceManager) return;
    const newMuted = !isMuted;
    voiceManager.toggleMute(newMuted);
    setIsMuted(newMuted);
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
