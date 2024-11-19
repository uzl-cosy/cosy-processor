import { FunctionComponent, useEffect, useState } from "react";
import Logo from "../../assets/icon.svg";
import { Button } from "../components/Button";
import { useCosyStore } from "../hooks/useCosyStore";
import { useConfigStore } from "../hooks/useConfigStore";
import { useDeviceStore } from "../hooks/useDeviceStore";
import Warning from "../components/Warning";
import Spinner from "../components/Spinner";
import '../styles.css';

function Controller() {
  const { running, healthInfo, statusInfo, setRunning, setStatusInfo, setHealthInfo } = useCosyStore();

  const config = useConfigStore();

  const { microphoneConnected } = useDeviceStore();

  const startCosy = () => {
    var command = config.startCommand;
    if (config.microphoneName != "") {
      command = command.concat(` -m '${config.microphoneName}'`);
    }
    window.electronAPI.startCosy(command, config.workingDirectory);
    setRunning(true);
  };

  const stopCosy = () => {
    window.electronAPI.stopCosy();
    setRunning(false);

    // reset status in store, as loading is not reset somehow
    const resetStatus = statusInfo;
    resetStatus.loading = 0.0;
    setStatusInfo(resetStatus);
    const resetHealth = healthInfo;
    resetHealth.cpuLoad = 0;
    resetHealth.memoryLoad = 0;
    setHealthInfo(resetHealth);
  };

  useEffect(() => {
    if (running && !microphoneConnected) {
      window.electronAPI.stopCosy();
      setRunning(false);

      return () => {
        console.log("Microphone lost. Stopping CoSy")
      };
    }

    return () => {};
  }, [running, microphoneConnected]);

  return (
    <div className="flex flex-col justify-center items-center w-full">
      <div className="flex flex-row items-center justify-center gap-10 mt-10">
        <Logo style={{ width: 250, height: 250 }} />
        {statusInfo.loading < 1.0 ? (
          !running ? (
          <Button onClick={() => startCosy()} disabled={!microphoneConnected}>
            Start 🚀
          </Button>
          ) : <div className="loading-container flex flex-col justify-center items-center gap-3">
                <div>Loading</div>
                <Spinner />
              </div>
        ) : (
            <div className="flex flex-col gap-5">
              <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6 w-44">
                <dt className="truncate text-sm font-medium text-gray-500">
                  CPU
                </dt>
                <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                  {healthInfo.cpuLoad.toFixed(2)} %
              </dd>
              </div>
              <div className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
                <dt className="truncate text-sm font-medium text-gray-500">
                  Arbeitsspeicher
                </dt>
                <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">
                  {healthInfo.memoryLoad.toFixed(2)} %
                </dd>
              </div>
              <Button onClick={() => stopCosy()}>Stopp ✋</Button>
            </div>
        )}
      </div>

      {!microphoneConnected && (
        <Warning message="Mikrofon nicht angeschlossen" className="mt-10" />
      )}
    </div>
  );
}

export default Controller as FunctionComponent;
