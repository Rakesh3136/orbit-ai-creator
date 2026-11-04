"use client";

import { useEffect, useState } from "react";
import { Download, X } from "lucide-react";

type InstallPrompt = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: "accepted" | "dismissed" }> };

export function PwaInstallButton() {
  const [promptEvent, setPromptEvent] = useState<InstallPrompt | null>(null);
  const [showGuide, setShowGuide] = useState(false);
  const [installed, setInstalled] = useState(false);

  useEffect(() => {
    const capture = (event: Event) => {
      event.preventDefault();
      setPromptEvent(event as InstallPrompt);
    };
    const onInstalled = () => { setInstalled(true); setPromptEvent(null); setShowGuide(false); };
    if (window.matchMedia("(display-mode: standalone)").matches) setInstalled(true);
    window.addEventListener("beforeinstallprompt", capture);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", capture);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  async function install() {
    if (!promptEvent) { setShowGuide(true); return; }
    await promptEvent.prompt();
    const choice = await promptEvent.userChoice;
    if (choice.outcome === "accepted") setInstalled(true);
    setPromptEvent(null);
  }

  return <>
    {!installed && <button className="install-button" onClick={install}><Download size={14} /> {promptEvent ? "Install AIMN" : "Install help"}</button>}
    {showGuide && <div className="install-guide-backdrop" role="presentation" onClick={() => setShowGuide(false)}>
      <section className="install-guide" role="dialog" aria-modal="true" aria-labelledby="install-guide-title" onClick={(event) => event.stopPropagation()}>
        <button className="install-guide-close" aria-label="Close install instructions" onClick={() => setShowGuide(false)}><X size={18} /></button>
        <p className="eyebrow">AIMN ANDROID APP</p>
        <h2 id="install-guide-title">Add AIMN to your home screen</h2>
        <ol>
          <li>Open the AIMN website in <b>Google Chrome</b> on your Android phone.</li>
          <li>Tap Chrome's <b>⋮ menu</b> in the top-right corner.</li>
          <li>Choose <b>Install app</b> or <b>Add to Home screen</b>.</li>
          <li>Confirm. AIMN opens in its own app window.</li>
        </ol>
        <p className="install-guide-note">Installation requires a deployed HTTPS website. If these options are missing, the website may not yet be deployed securely or Chrome has not marked it installable.</p>
        <button className="primary-button" onClick={() => setShowGuide(false)}>Got it</button>
      </section>
    </div>}
  </>;
}
