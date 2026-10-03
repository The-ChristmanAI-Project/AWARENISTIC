package org.christmanai.awarenistic

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
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
    private const val TRUSTED = "trusted"
    const val EXTRA_CARD = "card"
    const val EXTRA_WHO = "who"

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

    /** Where her card goes to the person they trust. Written by her mind; she never sends it. */
    data class Route(
        val ok: Boolean,
        val kind: String,
        val to: String,
        val subject: String,
        val body: String,
        val reason: String,
    )

    data class Reading(
        val status: String,
        val level: String,
        val who: String,
        val message: String,
        val cardText: String,
        val trusted: Route,
    )

    /** Her mind reads one message against the whole thread with that sender. */
    fun read(context: Context, text: String, who: String): Reading {
        val ledger = File(context.filesDir, "awarenistic-ledger.jsonl").absolutePath
        val answer = Python.getInstance()
            .getModule("phone_door")
            .callAttr("read", text, who, ledger, trusted(context))
            .toString()
        val o = JSONObject(answer)
        val t = o.optJSONObject("trusted") ?: JSONObject()
        return Reading(
            o.optString("status"),
            o.optString("level"),
            o.optString("who"),
            o.optString("message"),
            o.optString("card_text"),
            Route(
                t.optBoolean("ok"),
                t.optString("kind"),
                t.optString("to"),
                t.optString("subject"),
                t.optString("body"),
                t.optString("reason"),
            ),
        )
    }

    /** Her standing card for one stranger, routed to the person they trust. */
    fun routeFor(context: Context, who: String): Route {
        val ledger = File(context.filesDir, "awarenistic-ledger.jsonl").absolutePath
        val t = JSONObject(
            Python.getInstance().getModule("phone_door")
                .callAttr("route_for", who, ledger, trusted(context)).toString(),
        )
        return Route(
            t.optBoolean("ok"), t.optString("kind"), t.optString("to"),
            t.optString("subject"), t.optString("body"), t.optString("reason"),
        )
    }

    /** The one person they trust, named once, kept on this phone only. */
    fun trusted(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(TRUSTED, "").orEmpty()

    fun setTrusted(context: Context, contact: String) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putString(TRUSTED, contact.trim()).apply()
    }

    /**
     * Opens their own texting or mail app with her card written in, addressed to the person they trust.
     * The person presses send. Null when there is no one to send it to.
     */
    fun showSomeoneITrust(route: Route): Intent? {
        if (!route.ok) return null
        return when (route.kind) {
            "text" -> Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:" + Uri.encode(route.to)))
                .putExtra("sms_body", route.body)
            "mail" -> Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:" + Uri.encode(route.to)))
                .putExtra(Intent.EXTRA_EMAIL, arrayOf(route.to))
                .putExtra(Intent.EXTRA_SUBJECT, route.subject)
                .putExtra(Intent.EXTRA_TEXT, route.body)
            else -> null
        }
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
            .putExtra(EXTRA_WHO, reading.who)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        val tap = PendingIntent.getActivity(
            context, reading.who.hashCode(), open,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val builder = Notification.Builder(context, CHANNEL)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(reading.message.ifBlank { "Awarenistic" })
            .setContentText(reading.who)
            .setStyle(Notification.BigTextStyle().bigText(reading.cardText))
            .setContentIntent(tap)
            .setAutoCancel(true)
        showSomeoneITrust(reading.trusted)?.let { share ->
            val send = PendingIntent.getActivity(
                context, reading.who.hashCode() + 1, share.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
            )
            builder.addAction(
                Notification.Action.Builder(null, "Show someone I trust", send).build(),
            )
        }
        val note = builder.build()
        context.getSystemService(NotificationManager::class.java).notify(reading.who.hashCode(), note)
    }
}
