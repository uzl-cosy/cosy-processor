import { HiExclamationTriangle } from "react-icons/hi2";

/**
 * A warning component
 *
 * @param message The warning message
 * @param className The class name
 * @returns The warning component
 */
export default function Warning({
  message,
  className,
}: {
  message: string;
  className?: string;
}) {
  return (
    <div className={className + " rounded-md bg-yellow-50 p-4"}>
      <div className="flex">
        <div className="flex-shrink-0">
          <HiExclamationTriangle
            className="h-5 w-5 text-yellow-400"
            aria-hidden="true"
          />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-yellow-800">{message}</h3>
        </div>
      </div>
    </div>
  );
}
