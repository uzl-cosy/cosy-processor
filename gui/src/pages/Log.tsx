import { FunctionComponent, useEffect, useRef, useState } from "react";
import { useLogStore } from "../hooks/useLogStore";
import { useConfigStore } from "../hooks/useConfigStore";
import { HiBarsArrowDown, HiCloudArrowUp } from "react-icons/hi2";
// import { spawn } from 'child_process';
import axios from 'axios';
import FormData from 'form-data';

function Log() {
  const { log } = useLogStore();
  const config = useConfigStore();

  const logRef = useRef<null | HTMLDivElement>(null);
  const logEndRef = useRef<null | HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const [scrollBarVisible, setScrollBarVisible] = useState(false);
  const [logHasContent, setLogHasContent] = useState(false);

  async function sendLogs() {
    const logString = JSON.stringify(log);
    const form = new FormData();
    form.append('file', new Blob([logString], { type: 'application/json' }), 'log.json');
    if (!logHasContent) {
      return;
    }
    try {
      const response = await axios.post('https://cosy.uni-luebeck.de:3011/log', form, { 
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } catch (error) {
      console.error('Error while uploading log:', error);
    }
  }

  useEffect(() => {
    if (logEndRef.current && autoScroll) {
      logEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [log]);

  useEffect(() => {
    if (logRef.current) {
      setScrollBarVisible(
        logRef.current.scrollHeight > logRef.current.clientHeight
      );
    }
  }, [log]);

  useEffect(() => {
    if (Object.keys(log).length > 0) {
      setLogHasContent(true);
    }
  }, [log]);

  return (
    <div className="flex-1 overflow-hidden h-full relative">
      <div
        ref={logRef}
        className="text-[10px] h-full rounded-md ring-1 ring-inset ring-gray-800 text-white bg-black font-mono w-full p-2 overflow-x-hidden overflow-y-auto"
      >
        {log.length === 0 && <span>Bisher keine Logs ...</span>}
        {log.map((entry, index) => {
          if (entry.type === "stdout") {
            return (
              <span key={index} className="text-green-400 block">
                {entry.data}
              </span>
            );
          } else if (entry.type === "stderr") {
            return (
              <span key={index} className="text-red-400 block">
                {entry.data}
              </span>
            );
          } else if (entry.type === "exit") {
            return (
              <span key={index} className="text-yellow-400 block">
                {entry.data}
              </span>
            );
          }
        })}
        <div ref={logEndRef}></div>
      </div>
      <div>
        <button
          onClick={() => {
            sendLogs();
          }}
          className={`absolute bottom-3 right-6 text-black p-1 rounded-md ${
            logHasContent ? "bg-gray-200" : "bg-gray-400"
          }`}
          >
            <HiCloudArrowUp />
          </button>
      </div>
      {scrollBarVisible && (
        <div>
          <button
            onClick={() => {
              setAutoScroll(!autoScroll);
            }}
            className={`absolute bottom-11 right-6 text-black p-1 rounded-md ${
              autoScroll ? "bg-gray-200" : "bg-gray-400"
            }`}
          >
            <HiBarsArrowDown />
          </button>
        </div>
      )}
    </div>
  );
}

export default Log as FunctionComponent;
