"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Props {

  open:boolean;

  value:string;

  onChange:(value:string)=>void;

  onSave:()=>void;

  onCancel:()=>void;

}

export default function RenameDialog({

  open,

  value,

  onChange,

  onSave,

  onCancel,

}:Props){

  if(!open) return null;

  return(

<div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center">

<div className="w-[500px] rounded-3xl bg-white p-8 shadow-2xl">

<h2 className="text-xl font-bold">

Rename Document

</h2>

<p className="mt-2 text-slate-500">

Choose a new filename.

</p>

<Input

className="mt-6"

value={value}

onChange={(e)=>onChange(e.target.value)}

/>

<div className="mt-8 flex justify-end gap-3">

<Button
variant="outline"
onClick={onCancel}
>

Cancel

</Button>

<Button
onClick={onSave}
>

Save

</Button>

</div>

</div>

</div>

  )

}