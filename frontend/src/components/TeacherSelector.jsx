import React from "react";

export default function TeacherSelector({ teacher, setTeacher }) {
  return (
    <div className="teacher-selector">
      {/* Option: Female Teacher */}
      <label className={`radio-label ${teacher === "female" ? "selected" : ""}`}>
        <input 
            type="radio" 
            name="teacher" 
            checked={teacher === "female"} 
            onChange={() => setTeacher("female")} 
        />
        <span>👩‍🏫 F</span>
      </label>
      {/* Option: Male Teacher */}
      <label className={`radio-label ${teacher === "male" ? "selected" : ""}`}>
        <input 
            type="radio" 
            name="teacher" 
            checked={teacher === "male"} 
            onChange={() => setTeacher("male")} 
        />
        <span>👨‍🏫 M</span>
      </label>
    </div>
  );
}