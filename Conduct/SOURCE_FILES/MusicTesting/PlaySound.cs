using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

public class PlaySound : MonoBehaviour
{
    public AudioSource sound;

    public void PlayAudio()
    {
        sound.mute = !sound.mute;
    }

    private void Start() {
        sound.mute = true;
    }

}
