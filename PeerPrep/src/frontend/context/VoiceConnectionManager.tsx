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

export class VoiceConnectionManager {
  private pc: RTCPeerConnection;
  private localStream: MediaStream | null = null;
  private remoteAudioEl: HTMLAudioElement | null = null;
  private signalingSocket: WebSocket;
  private readonly roomId: string;
  private readonly clientId: string;
  private polite = false; // Perfect-negotiation flag (set by role election)
  private makingOffer = false;
  private ignoreOffer = false;
  private statsTimer: number | null = null;

  constructor(signalingUrl: string, roomId: string) {
    this.roomId = roomId;
    this.clientId = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

    this.pc = new RTCPeerConnection({
      iceServers: [{ urls: [import.meta.env.VITE_ICE_SERVERS] }],
    });

    // Remote audio element
    this.remoteAudioEl = document.createElement('audio');
    this.remoteAudioEl.autoplay = true;
    this.remoteAudioEl.muted = false; // Ensure not muted
    this.remoteAudioEl.setAttribute('data-voice', 'remote');
    document.body.appendChild(this.remoteAudioEl);

    // Logs: state changes
    this.pc.onconnectionstatechange = () =>
      log.pc('connectionState →', this.pc.connectionState);
    this.pc.oniceconnectionstatechange = () =>
      log.ice('iceConnectionState →', this.pc.iceConnectionState);
    this.pc.onicegatheringstatechange = () =>
      log.ice('iceGatheringState →', this.pc.iceGatheringState);
    this.pc.onnegotiationneeded = async () => {
      log.pc('onnegotiationneeded (makingOffer)', this.makingOffer);
      try {
        this.makingOffer = true;
        const offer = await this.pc.createOffer();
        await this.pc.setLocalDescription(offer);
        this.send({
          type: 'offer',
          roomId: this.roomId,
          sdp: this.pc.localDescription!,
          clientId: this.clientId,
        });
        log.sig('Sent offer');
      } catch (e) {
        log.err('onnegotiationneeded failed', e);
      } finally {
        this.makingOffer = false;
      }
    };

    // Remote track
    this.pc.ontrack = (ev) => {
      const [stream] = ev.streams;
      if (this.remoteAudioEl) this.remoteAudioEl.srcObject = stream;
      log.trk('ontrack:', ev.track.kind, 'streams:', ev.streams.length);
    };

    // ICE
    this.pc.onicecandidate = (ev) => {
      if (ev.candidate) {
        this.send({
          type: 'ice',
          roomId: this.roomId,
          candidate: ev.candidate.toJSON(),
          clientId: this.clientId,
        });
        log.ice('Sent ICE candidate');
      } else {
        log.ice('ICE gathering complete');
      }
    };

    // Signaling
    this.signalingSocket = new WebSocket(signalingUrl);
    this.signalingSocket.onopen = () => {
      log.sig('WS open; join room', this.roomId, 'clientId', this.clientId);
      this.send({ type: 'join', roomId: this.roomId, clientId: this.clientId });
      // simple role election: both announce hello; lower clientId becomes "impolite" offerer
      this.send({
        type: 'hello',
        roomId: this.roomId,
        clientId: this.clientId,
      });
    };

    this.signalingSocket.onmessage = async (evt) => {
      const msg = safeParse<SignalMsg>(evt.data);
      if (!msg || msg.roomId !== this.roomId || msg.clientId === this.clientId)
        return;

      switch (msg.type) {
        case 'hello': {
          // Role election
          // If their id is greater than ours → we are "impolite"(offerer); else "polite"(responder)
          // We only set this once (first hello we see).
          if (this.polite === false && this.pc.signalingState === 'stable') {
            this.polite = this.clientId > msg.clientId; // true if we should be responder
            log.sig(
              'Role elected. polite?',
              this.polite,
              '(ourId,peerId)=',
              this.clientId,
              msg.clientId
            );
          }
          break;
        }
        case 'offer': {
          log.sig(
            'Recv offer; signalingState=',
            this.pc.signalingState,
            'polite=',
            this.polite,
            'makingOffer=',
            this.makingOffer
          );
          const offerCollision =
            !this.polite &&
            (this.makingOffer || this.pc.signalingState !== 'stable');
          this.ignoreOffer = offerCollision;
          if (this.ignoreOffer) {
            log.sig('Ignoring offer (collision)');
            return;
          }
          try {
            await this.pc.setRemoteDescription(msg.sdp);
            const answer = await this.pc.createAnswer();
            await this.pc.setLocalDescription(answer);
            this.send({
              type: 'answer',
              roomId: this.roomId,
              sdp: this.pc.localDescription!,
              clientId: this.clientId,
            });
            log.sig('Sent answer');
          } catch (e) {
            log.err('Error handling offer', e);
          }
          break;
        }
        case 'answer': {
          log.sig('Recv answer; signalingState=', this.pc.signalingState);
          try {
            await this.pc.setRemoteDescription(msg.sdp);
          } catch (e) {
            log.err('Error handling answer', e);
          }
          break;
        }
        case 'ice': {
          try {
            await this.pc.addIceCandidate(msg.candidate);
            log.ice('Added remote ICE');
          } catch (e) {
            if (!this.ignoreOffer) log.err('Error adding ICE', e);
          }
          break;
        }
      }
    };

    this.signalingSocket.onerror = (e) => log.err('WS error', e);
    this.signalingSocket.onclose = () => log.sig('WS closed');

    // Periodic stats: see bytes flowing
    // this.startStats();
  }

  /** Initialize mic and attach to PC (sendrecv) */
  async initLocalMic(): Promise<void> {
    log.trk('Requesting getUserMedia({audio:true})...');
    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });
    const track = this.localStream.getAudioTracks()[0];
    if (!track) {
      log.err('No audio track from getUserMedia');
      return;
    }
    // Ensure a sendrecv transceiver
    const trans = this.ensureAudioTransceiver();
    // Attach track
    const sender = this.pc.addTrack(track, this.localStream);
    log.trk(
      'Attached local audio track. transceiver dir:',
      trans?.direction,
      'sender:',
      sender ? 'ok' : 'null'
    );

    // Start muted by default (optional)
    track.enabled = false;
    log.trk('Local mic initial enabled=', track.enabled);
  }

  /** Start call: only useful if we are the "offerer" (impolite) */
  async startCall(): Promise<void> {
    // If we’re the *offerer*, makingOffer happens in onnegotiationneeded automatically.
    // But we can poke it by calling setLocalDescription of an offer if stable.
    if (this.pc.signalingState !== 'stable') {
      log.pc('startCall skipped; signalingState=', this.pc.signalingState);
      return;
    }
    log.pc('startCall: creating offer proactively');
    try {
      this.makingOffer = true;
      const offer = await this.pc.createOffer();
      await this.pc.setLocalDescription(offer);
      this.send({
        type: 'offer',
        roomId: this.roomId,
        sdp: this.pc.localDescription!,
        clientId: this.clientId,
      });
      log.sig('Sent offer (manual)');
    } catch (e) {
      log.err('startCall failed', e);
    } finally {
      this.makingOffer = false;
    }
  }

  /** Toggle mute state of mic */
  toggleMute(mute: boolean) {
    const track = this.localStream?.getAudioTracks()[0];
    if (!track) {
      log.trk('toggleMute: no local track');
      return;
    }
    track.enabled = !mute;
    log.trk(
      'toggleMute →',
      mute ? 'MUTED' : 'UNMUTED',
      'track.enabled=',
      track.enabled
    );
  }

  /** Expose local stream for UI analyser */
  getLocalStream(): MediaStream | null {
    return this.localStream;
  }

  /** Cleanup */
  cleanup() {
    log.pc('cleanup()');
    if (this.statsTimer) {
      window.clearInterval(this.statsTimer);
      this.statsTimer = null;
    }
    this.localStream?.getTracks().forEach((t) => t.stop());
    this.pc.getSenders().forEach((s) => {
      if (s.track) {
        s.replaceTrack(null);
      }
    });
    this.pc.close();
    if (this.remoteAudioEl) {
      this.remoteAudioEl.remove();
      this.remoteAudioEl = null;
    }
    this.signalingSocket.close();
  }

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

  // private startStats() {
  //   this.statsTimer = window.setInterval(async () => {
  //     try {
  //       const stats = await this.pc.getStats();
  //       let outBytes = 0,
  //         inBytes = 0,
  //         outP = 0,
  //         inP = 0;
  //       stats.forEach((r) => {
  //         if (r.type === 'outbound-rtp' && (r as any).kind === 'audio') {
  //           outBytes += (r as any).bytesSent ?? 0;
  //           outP += (r as any).packetsSent ?? 0;
  //         }
  //         if (r.type === 'inbound-rtp' && (r as any).kind === 'audio') {
  //           inBytes += (r as any).bytesReceived ?? 0;
  //           inP += (r as any).packetsReceived ?? 0;
  //         }
  //       });
  //       log.st(
  //         'audio bytes sent/recv =',
  //         outBytes,
  //         '/',
  //         inBytes,
  //         ' packets=',
  //         outP,
  //         '/',
  //         inP
  //       );
  //     } catch (e) {
  //       // ignore
  //     }
  //   }, 2000);
  // }
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
