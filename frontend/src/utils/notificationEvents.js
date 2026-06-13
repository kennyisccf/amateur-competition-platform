export const NOTIFICATION_REFRESH_EVENT = 'lesai:notification-refresh'
export const NOTIFICATION_SYNC_EVENT = 'lesai:notification-sync'

export const getUnreadNotificationCount = (messages = []) =>
  messages.filter(item => item.action_required || item.friend_user_id).length

export const notifyNotificationsChanged = () => {
  window.dispatchEvent(new CustomEvent(NOTIFICATION_REFRESH_EVENT))
}

export const syncNotificationBadge = (messages = []) => {
  window.dispatchEvent(new CustomEvent(NOTIFICATION_SYNC_EVENT, {
    detail: {
      count: getUnreadNotificationCount(messages)
    }
  }))
}
