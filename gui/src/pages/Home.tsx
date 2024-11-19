import { FunctionComponent, useEffect, useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { HiCog8Tooth, HiCommandLine, HiCpuChip } from "react-icons/hi2";
import { useLogStore } from "../hooks/useLogStore";
import axios from "axios";
import { useQuery } from "react-query";
import { useCosyStore } from "../hooks/useCosyStore";
import { useConfigStore } from "../hooks/useConfigStore";
import { useDeviceStore } from "../hooks/useDeviceStore";

const fetchHealthInfo = async () => {
  try {
    const { data } = await axios.get("http://localhost:8000/health");
    return data;
  } catch (error) {
    throw new Error("Failed to fetch health info");
  }
};

const fetchStatusInfo = async () => {
  try {
    const { data } = await axios.get("http://localhost:8000/status");
    return data;
  } catch (error) {
    throw new Error("Failed to fetch status info");
  }
};

function Home() {
  const { addLog } = useLogStore();

  const { running, setHealthInfo, setStatusInfo, setRunning } = useCosyStore();

  const { microphoneConnected, setMicrophoneConnected } = useDeviceStore();

  const [micName, setMicName] = useState(
    useConfigStore.getState().microphoneName
  );

  const checkMic = () => {
    setMicName(useConfigStore.getState().microphoneName);
    navigator.mediaDevices
      .enumerateDevices()
      .then((devices) => {
        const isMicrophoneConnected = devices.some((device) =>
          // Mic is considered connected if the given name is included in one device name and .kind is "audioinput"
          // uses inlcude() so it can use substrings (DJI mics have a serial number in their name)
          device.label.toLowerCase().includes(micName.toLowerCase()) && device.kind == "audioinput"
        );

        setMicrophoneConnected(isMicrophoneConnected);
      })
      .catch((error) => console.error("Failed to enumerate devices", error));
  };

  useQuery("health", fetchHealthInfo, {
    refetchInterval: 1000,
    onSuccess: (data) => {
      setHealthInfo(data);
      setRunning(true);
    },
    onError: () => setRunning(false),
  });

  useQuery("status", fetchStatusInfo, {
    refetchInterval: 1000,
    onSuccess: (data) => {
      setStatusInfo(data);
    },
    onError: () => {},
  });

  useEffect(() => {
    window.electronAPI.onCosyStdout((data) => addLog({ type: "stdout", data }));
    window.electronAPI.onCosyStderr((data) => addLog({ type: "stderr", data }));
    window.electronAPI.onCosyExit((data) =>
      addLog({ type: "exit", data: `CoSy exited with code ${data}` })
    );
  }, [addLog]);

  useEffect(() => {
    // Add event listener for mediaDevices change
    navigator.mediaDevices.addEventListener("devicechange", checkMic);
    checkMic();

    // Clean-up function to remove event listener when component unmounts
    return () => {
      navigator.mediaDevices.removeEventListener("devicechange", checkMic);
    };
  }, [micName]);

  useEffect(() => {
    const unsubscribe = useConfigStore.subscribe((state) => {
      const { microphoneName } = state;
      setMicName(microphoneName);
    });

    // Clean-up function to unsubscribe when the component unmounts
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(() => {
        // Microphone access granted
        console.log("Microphone access granted.");
      })
      .catch((error) => {
        // Microphone access denied
        console.error("Microphone access denied:", error);
      });
  }, []);

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="w-full flex justify-end gap-3 text-white text-3xl mb-10 ">
        <Link to="/">
          <HiCpuChip className="hover:opacity-80 transition drop-shadow-sm" />
        </Link>
        <Link to="log">
          <HiCommandLine className="hover:opacity-80 transition drop-shadow-sm" />
        </Link>
        <Link to="settings">
          <HiCog8Tooth className="hover:opacity-80 transition drop-shadow-sm" />
        </Link>
      </div>
      <Outlet />
    </div>
  );
}

export default Home as FunctionComponent;
