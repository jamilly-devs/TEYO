// Destructive actions (delete task/event/market item) require explicit
// confirmation before the request is sent — BUSINESS_RULES.md #4.
export function ConfirmDialog({
  message,
  onConfirm,
  onCancel,
}: {
  message: string
  onConfirm: () => void
  onCancel: () => void
}) {
  return (
    <div className="confirm-overlay" role="dialog" aria-modal="true">
      <div className="confirm-box">
        <p>{message}</p>
        <button type="button" onClick={onConfirm}>
          Confirmar
        </button>
        <button type="button" onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </div>
  )
}
