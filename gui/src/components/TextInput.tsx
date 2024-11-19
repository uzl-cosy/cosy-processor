import { InputHTMLAttributes } from "react";

/**
 * A text input component
 *
 * @param title The title
 * @returns The text input component
 */
export default function TextInput({
  title,
  ...rest
}: {
  title: string;
} & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="rounded-md px-3 pb-1.5 pt-2.5 shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-offset-teal-600 bg-white">
      <label htmlFor="name" className="block text-xs font-medium text-gray-900">
        {title}
      </label>
      <input
        {...rest}
        type="text"
        className="block w-full border-0 p-0 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
      />
    </div>
  );
}
