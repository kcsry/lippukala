/* eslint-disable max-classes-per-file */

/* globals BarcodeDetector */

class PosQRNative {
  constructor() {
    this.barcodeDetector = new BarcodeDetector({ formats: ["qr_code"] });
  }

  async init() {
    return Boolean(this.barcodeDetector);
  }

  async detectFromVideo(video) {
    return this.barcodeDetector.detect(video);
  }
}

class PosQR {
  static hasBarcodeDetector() {
    return typeof BarcodeDetector !== "undefined";
  }

  constructor({ addLogEntry, onFoundQRCode }) {
    this.addLogEntry = addLogEntry;
    this.onFoundQRCode = onFoundQRCode;

    const video = document.createElement("video");
    video.id = "posqr-video";
    document.body.appendChild(video);

    this.video = video;
    this.detecting = false;
    this.detector = null;
    this.interval = null;
    this.media = null;
  }

  async init() {
    if (PosQR.hasBarcodeDetector()) {
      this.addLogEntry("Käytetään sisäänrakennettua QR-koodinlukijaa");
      this.detector = new PosQRNative();
    } else {
      this.addLogEntry("Ei QR-koodinlukijaa");
      throw new Error("No QR code detector");
    }
    await this.detector.init();
    this.addLogEntry("QR-koodinlukija valmis");
  }

  updateDOM() {
    const started = this.isStarted();
    document.body.classList.toggle("qr-started", started);
  }

  isStarted() {
    return Boolean(this.media) && Boolean(this.interval);
  }

  isInitialized() {
    return Boolean(this.detector);
  }

  async doDetectQR() {
    const { video } = this;
    try {
      if (this.detecting) {
        console.warn("Already detecting");
        return;
      }
      this.detecting = true;
      const t0 = performance.now();
      for (const barcode of await this.detector.detectFromVideo(video)) {
        this.onFoundQRCode(barcode);
      }
      const t1 = performance.now();
      console.debug("QR detect time", Math.round(t1 - t0));
    } finally {
      this.detecting = false;
    }
  }

  async start() {
    if (!this.isInitialized()) await this.init();
    await this.stop();
    try {
      this.media = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          frameRate: { ideal: 10 },
        },
        audio: false,
      });
      this.video.srcObject = this.media;
      await this.video.play();
      this.addLogEntry("Kamera käynnistetty");
      this.interval = setInterval(() => this.doDetectQR(), 300);
    } catch (err) {
      this.addLogEntry(`QR-koodinlukijan käynnistäminen epäonnistui: ${err}`);
    }
    this.updateDOM();
  }

  async stop() {
    if (this.media) {
      for (const track of this.media.getTracks()) {
        track.stop();
      }
      this.media = null;
    }
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.updateDOM();
  }
}

window.PosQR = PosQR;
