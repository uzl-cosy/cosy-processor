import { FunctionComponent } from "react";
import TextInput from "../components/TextInput";
import { useConfigStore } from "../hooks/useConfigStore";

function Settings() {
  const config = useConfigStore();
  return (
    <div className="flex flex-col gap-5">
      <TextInput
        title="Startbefehl"
        placeholder="python3 main.py -c config.yml"
        value={config.startCommand}
        onChange={(e) => config.setStartCommand(e.target.value)}
      />
      <TextInput
        title="Arbeitsverzeichnis"
        placeholder="~/laboratorium-cosy-v2"
        value={config.workingDirectory}
        onChange={(e) => config.setWorkingDirectory(e.target.value)}
      />
      <TextInput
        title="Mikrofonname"
        placeholder="USB Audio Device"
        value={config.microphoneName}
        onChange={(e) => config.setMicrophoneName(e.target.value)}
      />
    </div>
  );
}

export default Settings as FunctionComponent;
