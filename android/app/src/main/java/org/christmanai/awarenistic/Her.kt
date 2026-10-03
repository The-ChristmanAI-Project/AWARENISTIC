package org.christmanai.awarenistic

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import com.chaquo.python.Python
import org.json.JSONObject
import java.io.File

/**
 * The phone's side of her. Hands a message to her mind, which runs on this phone,
 * and speaks up with her card when a script shows itself. Nothing leaves the phone.
 */
object Her {
    private const val CHANNEL = "awarenistic"
    private const val PREFS = "awarenistic"
    private const val WATCHED = "watched"
    const val EXTRA_CARD = "card"

    /** The apps the scams run through. The person chooses which ones she watches. */
    val WATCHABLE: LinkedHashMap<String, String> = linkedMapOf(
        "com.whatsapp" to "WhatsApp",
        "com.whatsapp.w4b" to "WhatsApp Business",
        "com.facebook.orca" to "Messenger",
        "com.facebook.katana" to "Facebook",
        "org.telegram.messenger" to "Telegram",
        "com.instagram.android" to "Instagram",
        "org.thoughtcrime.securesms" to "Signal",
        "com.viber.voip" to "Viber",
        "jp.naver.line.android" to "LINE",
        "com.snapchat.android" to "Snapchat",
        "com.tinder" to "Tinder",
        "com.bumble.app" to "Bumble",
        "co.hinge.app" to "Hinge",
    )

    data class Reading(
        val status: String,
        val level: String,
        val who: String,
        val message: String,
        val cardText: String,
    )

    /** Her mind reads one message against the whole thread with that sender. */
    fun read(context: Context, text: String, who: String): Reading {
        val ledger = File(context.filesDir, "awarenistic-ledger.jsonl").absolutePath
        val answer = Python.getInstance()
            .getModule("phone_door")
            .callAttr("read", text, who, ledger)
            .toString()
        val o = JSONObject(answer)
        return Reading(
            o.optString("status"),
            o.optString("level"),
            o.optString("who"),
            o.optString("message"),
            o.optString("card_text"),
        )
    }

    fun watched(context: Context): Set<String> =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getStringSet(WATCHED, WATCHABLE.keys) ?: WATCHABLE.keys

    fun setWatched(context: Context, packages: Set<String>) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putStringSet(WATCHED, HashSet(packages)).apply()
    }

    fun makeChannel(context: Context) {
        val channel = NotificationChannel(CHANNEL, "Awarenistic", NotificationManager.IMPORTANCE_HIGH)
        channel.description = "She speaks up when a message reads like a scam."
        context.getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    fun maySpeak(context: Context): Boolean =
        Build.VERSION.SDK_INT < 33 ||
            context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    /** Her card, right then, on the phone. Tapping it opens the full card. */
    fun speakUp(context: Context, reading: Reading) {
        if (!maySpeak(context)) return
        val open = Intent(context, MainActivity::class.java)
            .putExtra(EXTRA_CARD, reading.cardText)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        val tap = PendingIntent.getActivity(
            context, reading.who.hashCode(), open,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val note = Notification.Builder(context, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(reading.message.ifBlank { "Awarenistic" })
            .setContentText(reading.who)
            .setStyle(Notification.BigTextStyle().bigText(reading.cardText))
            .setContentIntent(tap)
            .setAutoCancel(true)
            .build()
        context.getSystemService(NotificationManager::class.java).notify(reading.who.hashCode(), note)
    }
}
