import type { FC } from 'react';

type InputTextProps = {
  label?: string;
  value: string;
  onChangeText: (val: string) => void;
  placeholder?: string;
};

export const InputText: FC<InputTextProps> = ({
  label,
  value,
  onChangeText,
  placeholder,
}) => {
  return (
    <div className="w-[20vw]">
      <label className="block mb-3 text-xl">{label}</label>
      <input
        className="border rounded px-3 py-2 w-full"
        type="text"
        value={value}
        onChange={(e) => onChangeText(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
};
