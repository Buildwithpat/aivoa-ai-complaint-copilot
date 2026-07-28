function TypingIndicator() {
  return (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((dot) => (
        <span
          key={dot}
          className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400"
          style={{ animationDelay: `${dot * 0.15}s` }}
        />
      ))}
    </div>
  )
}

export default TypingIndicator
