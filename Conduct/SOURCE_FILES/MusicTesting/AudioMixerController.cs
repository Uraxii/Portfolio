using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

public class AudioMixerController : MonoBehaviour
{
    public bool debug = false;
    public AudioMixer mixer;
    public AudioSource source;
    public AudioMixerSnapshot[] snapshots;
    public int[] segmentRepeats;
    public float[] transitionTimes;

    private float sourceLastTime = -1.0f;
    private int currentSnapshot = 0;
    private int segmentCounter = 0;
    // Update is called once per frame
    void Update()
    {
        if (source.time < sourceLastTime)
        {
            if (++segmentCounter == segmentRepeats[currentSnapshot])
            {
                segmentCounter = 0;
                currentSnapshot = (currentSnapshot + 1 ) % snapshots.Length;
                snapshots[currentSnapshot].TransitionTo(transitionTimes[currentSnapshot]);
            }
        }
        sourceLastTime = source.time;
    }

    void OnGUI()
    {
        if(debug)
        {
            int index = 0;
            foreach (var s in snapshots)
            {
                if (GUILayout.Button("Switch to snapshot " + s))
                {
                    segmentCounter = 0;
                    currentSnapshot = index;
                    snapshots[currentSnapshot].TransitionTo(transitionTimes[currentSnapshot]);
                }
                index++;
            }
        }
    }
}