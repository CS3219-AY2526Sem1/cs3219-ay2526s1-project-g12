## Usage log

### VoiceConnectionManager.tsx

- The prompt is "Please add debugging logs to VoiceConnectionManager.tsx"
- The output is:

  ````
  type SignalMsg =
  | { type: 'join'; roomId: string; clientId: string }
  | { type: 'hello'; roomId: string; clientId: string }
  | {
  type: 'offer';
  roomId: string;
  sdp: RTCSessionDescriptionInit;
  clientId: string;
  }
  | {
  type: 'answer';
  roomId: string;
  sdp: RTCSessionDescriptionInit;
  clientId: string;
  }
  | {
  type: 'ice';
  roomId: string;
  candidate: RTCIceCandidateInit;
  clientId: string;
  };

      const log = {
      sig: (...a: unknown[]) => console.log('[Signal]', ...a),
      pc: (...a: unknown[]) => console.log('[PC]', ...a),
      ice: (...a: unknown[]) => console.log('[ICE]', ...a),
      trk: (...a: unknown[]) => console.log('[Track]', ...a),
      st: (...a: unknown[]) => console.log('[Stats]', ...a),
      err: (...a: unknown[]) => console.error('[Error]', ...a),
      };
      ...
      // Logs: state changes
      this.pc.onconnectionstatechange = () =>
          log.pc('connectionState →', this.pc.connectionState);
      this.pc.oniceconnectionstatechange = () =>
          log.ice('iceConnectionState →', this.pc.iceConnectionState);
      this.pc.onicegatheringstatechange = () =>
          log.ice('iceGatheringState →', this.pc.iceGatheringState);
      this.pc.onnegotiationneeded = async () => {
          log.pc('onnegotiationneeded (makingOffer)', this.makingOffer);

      // ---------- helpers ----------

      private ensureAudioTransceiver(): RTCRtpTransceiver | null {
          // Reuse existing audio transceiver if any
          const existing = this.pc.getTransceivers
          ? this.pc
              .getTransceivers()
              .find(
                  (t) =>
                  t.receiver.track?.kind === 'audio' ||
                  t.sender.track?.kind === 'audio'
              )
          : null;
          if (existing) {
          // Ensure direction at least sendrecv for voice
          if (existing.direction !== 'sendrecv') {
              existing.direction = 'sendrecv';
          }
          return existing;
          }
          try {
          const t = this.pc.addTransceiver('audio', { direction: 'sendrecv' });
          log.trk('Created audio transceiver sendrecv');
          return t;
          } catch (e) {
          log.err('addTransceiver failed', e);
          return null;
          }
      }

      private send(msg: SignalMsg) {
          const raw = JSON.stringify(msg);
          try {
          this.signalingSocket.send(raw);
          } catch (e) {
          log.err('WS send failed', e);
          }
      }

      private startStats() {
          this.statsTimer = window.setInterval(async () => {
          try {
              const stats = await this.pc.getStats();
              let outBytes = 0,
              inBytes = 0,
              outP = 0,
              inP = 0;
              stats.forEach((r) => {
              if (r.type === 'outbound-rtp' && (r as any).kind === 'audio') {
                  outBytes += (r as any).bytesSent ?? 0;
                  outP += (r as any).packetsSent ?? 0;
              }
              if (r.type === 'inbound-rtp' && (r as any).kind === 'audio') {
                  inBytes += (r as any).bytesReceived ?? 0;
                  inP += (r as any).packetsReceived ?? 0;
              }
              });
              log.st(
              'audio bytes sent/recv =',
              outBytes,
              '/',
              inBytes,
              ' packets=',
              outP,
              '/',
              inP
              );
          } catch (e) {
              // ignore
          }
          }, 2000);
      }
      }

      function safeParse<T>(raw: unknown): T | null {
      if (typeof raw === 'string') {
          try {
          return JSON.parse(raw) as T;
          } catch {
          return null;
          }
      }
      // If it's already an object, trust the caller
      if (typeof raw === 'object' && raw !== null) {
          return raw as T;
      }
      return null;
      }
      ```
  ````

### signaling-svc/server.js

- The prompt is "Extends audio stream functionality to signaling server based on https://webrtc.org/getting-started/media-devices"
- The output is
  ```
  // VOICE MESSAGE SUPPORT
  case 'join':
  const topic = map.setIfUndefined(
      topics,
      message.roomId,
      () => new Set()
  );
  topic.add(conn);
  subscribedTopics.add(message.roomId);
  console.log(`Client joined room: ${message.roomId}`);
  break;
  case 'offer':
  case 'answer':
  case 'ice':
  const roomId = message.roomId;
  if (!roomId) return;
  const receivers = topics.get(roomId);
  if (receivers) {
      receivers.forEach((r) => {
      if (r !== conn) send(r, message);
      });
  }
  break;
  ```
