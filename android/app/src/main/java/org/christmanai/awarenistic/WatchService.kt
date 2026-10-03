package org.christmanai.awarenistic

import android.app.Notification
import android.os.Build
import android.os.Bundle
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import java.util.concurrent.Executors

/**
 * Sits beside the person. Every message that arrives in an app they chose to have her
 * watch is read by her mind on this phone. When a script shows itself she speaks up.
 * She never replies, never blocks, never sends anything anywhere.
 */
class WatchService : NotificationListenerService() {
    private val worker = Executors.newSingleThreadExecutor()
    private val seen = object : LinkedHashMap<String, Boolean>(512, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Boolean>?) = size > 500
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        if (sbn.packageName == packageName) return
        if (sbn.packageName !in Her.watched(this)) return
        val n = sbn.notification ?: return
        if (n.flags and Notification.FLAG_GROUP_SUMMARY != 0) return
        val app = Her.WATCHABLE[sbn.packageName] ?: sbn.packageName
        for ((sender, text) in messagesIn(n.extras)) {
            val who = "$sender · $app"
            val key = "$who|$text"
            val fresh = synchronized(seen) {
                if (seen.containsKey(key)) false else { seen[key] = true; true }
            }
            if (!fresh) continue
            worker.execute {
                try {
                    val reading = Her.read(this, text, who)
                    if (reading.level != "clear") Her.speakUp(this, reading)
                } catch (e: Exception) {
                    // Her mind refused or failed: say so in the log, never guess a verdict.
                    Log.e("Awarenistic", "could not read a message from $app", e)
                }
            }
        }
    }

    /** Each (sender, text) the notification carries. Messaging apps send the thread; others one line. */
    private fun messagesIn(extras: Bundle): List<Pair<String, String>> {
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString()?.trim().orEmpty()
        val out = mutableListOf<Pair<String, String>>()
        @Suppress("DEPRECATION")
        val bundles = extras.getParcelableArray(Notification.EXTRA_MESSAGES)
        if (bundles != null) {
            for (m in Notification.MessagingStyle.Message.getMessagesFromBundleArray(bundles)) {
                val text = m.text?.toString()?.trim().orEmpty()
                if (text.isEmpty()) continue
                val sender = if (Build.VERSION.SDK_INT >= 28) m.senderPerson?.name?.toString() else null
                out += (sender?.trim().takeUnless { it.isNullOrEmpty() } ?: title.ifEmpty { "unknown" }) to text
            }
        }
        if (out.isEmpty()) {
            val text = (extras.getCharSequence(Notification.EXTRA_BIG_TEXT)
                ?: extras.getCharSequence(Notification.EXTRA_TEXT))?.toString()?.trim().orEmpty()
            if (text.isNotEmpty()) out += title.ifEmpty { "unknown" } to text
        }
        return out
    }
}
