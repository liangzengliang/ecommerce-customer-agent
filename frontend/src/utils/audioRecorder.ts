/**
 * 语音录制工具
 * 基于浏览器 MediaRecorder API，可用于发送语音消息。
 */

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null
  private chunks: Blob[] = []

  /** 开始录制 */
  async start(): Promise<void> {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    this.mediaRecorder = new MediaRecorder(stream)
    this.chunks = []

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data)
    }

    this.mediaRecorder.start()
  }

  /** 停止录制并返回音频 Blob */
  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('未开始录制'))
        return
      }
      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: 'audio/webm' })
        this.chunks = []
        resolve(blob)
      }
      this.mediaRecorder.stop()
    })
  }

  /** 是否正在录制 */
  get isRecording(): boolean {
    return this.mediaRecorder?.state === 'recording'
  }
}