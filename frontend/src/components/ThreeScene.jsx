import React, { Suspense, useRef, useEffect, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF, Environment, Html, useAnimations } from "@react-three/drei";
import { MathUtils } from "three";
import { randInt } from "three/src/math/MathUtils";

/* ---------------- TEACHER CONFIGURATION ---------------- */
const TEACHER_CONFIG = {
  male: {
    position: [0, -2.0, 0],
    scale: 1.8,
    bubblePos: [0, 2.5, 0] // Higher bubble for Male
  },
  female: {
    position: [0, -1.6, 0],
    scale: 1.7,
    bubblePos: [0, 2.2, 0]
  },
};

const FADE = 0.5;

/* ---------------- RHUBARB MAPPING ---------------- */
const RHUBARB_TO_NUMERIC = {
  X: "0", A: "21", B: "19", C: "4", D: "2", E: "8", F: "7", G: "18", H: "14",
};

/* ---------------- CLIP DETECTOR ---------------- */
function detectClip(actions, tags = []) {
  if (!actions) return null;
  const keys = Object.keys(actions);
  const lowerKeys = keys.map((k) => k.toLowerCase());

  for (let tag of tags) {
    const foundIndex = lowerKeys.findIndex((k) => k.includes(tag));
    if (foundIndex >= 0) return keys[foundIndex];
  }

  // Fallback to idle
  const idleIndex = lowerKeys.findIndex((k) => k.includes("idle") || k.includes("stand"));
  if (idleIndex >= 0) return keys[idleIndex];

  return keys[0];
}

/* ---------------- MODEL COMPONENT ---------------- */
function TeacherModel({ teacher, lipSyncData, audioUrl, isRecording, loading, isMuted, reloadTrigger, audioEl }) {
  const head = useRef();

  // 1. USE ORIGINAL SEPARATE FILES
  const modelFile = teacher === "male" ? "male_teacher" : "female_teacher";
  const animFile = teacher === "male" ? "animations_male" : "animations_female";

  const { scene: modelScene } = useGLTF(`/models/${modelFile}.glb`, true);
  const { animations } = useGLTF(`/models/${animFile}.glb`, true);

  // 2. CLEAN INVALID TRACKS (Restored Old Logic)
  // This is the specific fix that makes your Male animation work!
  useEffect(() => {
    const valid = new Set();
    modelScene.traverse((n) => valid.add(n.name));

    animations.forEach((clip) => {
      clip.tracks = clip.tracks.filter((track) => {
        const node = track.name.split(".")[0];
        return valid.has(node);
      });
    });
  }, [modelScene, animations]);

  const { actions, mixer } = useAnimations(animations, modelScene);

  const [realDuration, setRealDuration] = useState(0);
  const [state, setState] = useState("Idle");

  const [blink, setBlink] = useState(false);
  const [dots, setDots] = useState(".");
  const blinkRef = useRef();
  const thinkRef = useRef();

  // --- Find Head Mesh ---
  useEffect(() => {
    head.current = null;
    modelScene.traverse((c) => {
      if (c.isMesh && c.morphTargetDictionary) {
        // Prioritize Head/Face
        if (c.name.includes("Head") || c.name.includes("Face") || !head.current) {
          head.current = c;
        }
      }
    });
  }, [modelScene, teacher]);

  // --- Audio Setup ---
  useEffect(() => {
    if (!audioUrl) {
      audioEl.pause();
      audioEl.src = "";
      setState((isRecording || loading) ? "Thinking" : "Idle");
      return;
    }

    // Reuse the same audio element
    audioEl.pause();
    audioEl.src = audioUrl;
    audioEl.load();

    const handleLoadedMetadata = () => { if (audioEl.duration) setRealDuration(audioEl.duration); };
    const handlePlay = () => { if (!isRecording && !loading && !isMuted) setState("Talking"); };
    const handlePause = () => { if (!isRecording && !loading) setState("Idle"); };
    const handleEnded = () => { if (!isRecording && !loading) setState("Idle"); };
    const handleCanPlayThrough = () => {
      if (!isMuted) {
        audioEl.play().catch(err => {
          console.warn("Auto-play blocked or failed:", err);
          // If blocked, the user can still click 'Reload' to play manually
        });
      }
    };

    audioEl.addEventListener("loadedmetadata", handleLoadedMetadata);
    audioEl.addEventListener("play", handlePlay);
    audioEl.addEventListener("pause", handlePause);
    audioEl.addEventListener("ended", handleEnded);
    audioEl.addEventListener("canplaythrough", handleCanPlayThrough);

    return () => {
      audioEl.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audioEl.removeEventListener("play", handlePlay);
      audioEl.removeEventListener("pause", handlePause);
      audioEl.removeEventListener("ended", handleEnded);
      audioEl.removeEventListener("canplaythrough", handleCanPlayThrough);
    };
  }, [audioUrl, teacher, isMuted]);

  // --- Mute Logic ---
  useEffect(() => {
    if (!audioEl) return;
    if (isMuted) {
      audioEl.pause();
      setState("Idle");
    } else {
      // Only resume if we have an audio URL and we are not recording/loading
      if (audioUrl && !isRecording && !loading && audioEl.paused && audioEl.currentTime > 0 && audioEl.currentTime < audioEl.duration) {
        audioEl.play().catch(() => { });
      }
    }
  }, [isMuted]);

  // --- Reload Logic ---
  useEffect(() => {
    if (!audioEl || reloadTrigger === 0) return;
    audioEl.currentTime = 0;
    if (!isMuted) audioEl.play().catch(() => { });
    else setState("Idle"); // Ensure idle if muted
  }, [reloadTrigger]);

  // --- State Logic ---
  useEffect(() => {
    if (isRecording || loading) {
      setState("Thinking");
      if (audioEl && !audioEl.paused) audioEl.pause();
    } else {
      if (isMuted) setState("Idle");
      else if (audioEl && !audioEl.paused) setState("Talking");
      else setState("Idle");
    }
  }, [isRecording, loading, isMuted]);

  // --- Blinking ---
  useEffect(() => {
    function loop() {
      blinkRef.current = setTimeout(() => {
        setBlink(true);
        setTimeout(() => setBlink(false), 120);
        loop();
      }, randInt(1500, 4200));
    }
    loop();
    return () => clearTimeout(blinkRef.current);
  }, [teacher]);

  // --- Dots Animation ---
  useEffect(() => {
    if (!isRecording && !loading) return setDots(".");
    let i = 1;
    thinkRef.current = setInterval(() => { i = i === 3 ? 1 : i + 1; setDots(".".repeat(i)); }, 420);
    return () => clearInterval(thinkRef.current);
  }, [isRecording, loading]);

  // --- Animation Mixer ---
  useEffect(() => {
    if (!actions) return;
    const idleClip = detectClip(actions, ["idle", "stand"]);
    const talkClip = detectClip(actions, ["talk", "speak"]);
    const thinkClip = detectClip(actions, ["think", "ponder"]);

    let targetClipName = idleClip;
    if (state === "Talking" && talkClip) targetClipName = talkClip;
    // Fallback to idle if thinking clip is missing
    if (state === "Thinking") targetClipName = thinkClip || idleClip;

    Object.values(actions).forEach((action) => {
      if (action.getClip().name !== targetClipName) action.fadeOut(FADE);
    });

    if (actions[targetClipName]) actions[targetClipName].reset().fadeIn(FADE).play();
  }, [actions, state, teacher]);

  // --- Reset Morphs ---
  useEffect(() => {
    if (mixer) mixer.stopAllAction();
    if (head.current?.morphTargetInfluences) head.current.morphTargetInfluences.fill(0);
  }, [teacher]);

  const morph = (name, v, sp = 0.2) => {
    if (!head.current) return;
    const dict = head.current.morphTargetDictionary;
    const infl = head.current.morphTargetInfluences;
    if (dict && dict[name] !== undefined) {
      infl[dict[name]] = MathUtils.lerp(infl[dict[name]], v, sp);
    }
  };

  useFrame(() => {
    // 1. Blinking
    morph("eye_close", blink ? 1 : 0, 0.25);

    // 2. Reset Mouth (Faster close for snappy lips)
    if (head.current?.morphTargetDictionary) {
      for (let i = 0; i <= 21; i++) morph(i.toString(), 0, 0.4);
    }

    // 3. LIP SYNC FIX (Lookahead + Faster Morph)
    if (state === "Talking" && audioEl && !audioEl.paused && lipSyncData?.mouthCues && realDuration > 0) {
      // LOOKAHEAD: We check 0.1s into the future
      const currentAudioTime = audioEl.currentTime + 0.1;

      const estimatedDuration = lipSyncData.metadata?.duration || realDuration;
      const normalizedTime = (currentAudioTime / realDuration) * estimatedDuration;

      const cue = lipSyncData.mouthCues.find((c) => normalizedTime >= c.start && normalizedTime <= c.end);
      if (cue) {
        const targetKey = RHUBARB_TO_NUMERIC[cue.value];
        // FASTER SPEED: 0.8 instead of 0.6
        if (targetKey) morph(targetKey, 1.0, 0.8);
      }
    }
  });

  const config = TEACHER_CONFIG[teacher];

  return (
    <group position={config.position} scale={config.scale}>
      {/* Dynamic Bubble Position */}
      {(isRecording || loading) && (
        <Html position={config.bubblePos}>
          <div className="flex justify-center relative">
            <span className="animate-ping absolute h-10 w-10 rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative h-10 w-10 rounded-full bg-white shadow flex items-center justify-center text-blue-500 font-bold text-xl">{dots}</span>
          </div>
        </Html>
      )}
      <primitive object={modelScene} />
    </group>
  );
}

export default function ThreeScene(props) {
  return (
    <Canvas camera={{ position: [0, 0, 2.5], fov: 35 }}>
      <ambientLight intensity={0.6} />
      <directionalLight intensity={1.2} position={[5, 5, 5]} />
      <Suspense key={props.teacher} fallback={null}>
        <TeacherModel
          {...props}
          isMuted={props.isMuted}
          reloadTrigger={props.reloadTrigger}
          audioEl={props.audioEl}
        />
        <Environment preset="city" />
      </Suspense>
      <OrbitControls enableZoom={false} enablePan={false} target={[0, 0.2, 0]} />
    </Canvas>
  );
}