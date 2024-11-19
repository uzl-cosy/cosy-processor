import { spawn, ChildProcess } from "child_process";

/**
 * Split a command string into a program and its arguments
 * @param cmd The command string to split
 * @returns An object with the program and its arguments
 */
function splitCommand(cmd: string) {
  // Split the command string into parts
  const parts = cmd.match(/(?:[^\s"]+|"[^"]*")+/g);

  // The first part is the program
  const program = parts[0];

  // The rest are the arguments
  const args = parts.slice(1).map((arg) => arg.replace(/"/g, ""));

  return { program, args };
}

/**
 * Create a new Cosy process
 * @param command The command to run
 * @param cwd The working directory
 * @returns The Cosy process
 */
export function createCosyProcess(command: string, cwd: string): ChildProcess {
  const { program, args } = splitCommand(command);
  const cosyProcess = spawn(program, args, {
    stdio: ["ignore", "pipe", "pipe"],
    cwd: cwd,
    shell: true,
  });

  return cosyProcess;
}
