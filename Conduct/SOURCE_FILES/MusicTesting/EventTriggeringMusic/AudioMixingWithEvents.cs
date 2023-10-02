using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

public class AudioMixingWithEvents : MonoBehaviour
{
    public float pauseFilterCutoff;
    public float pauseFilterCutoffDuration;
    public AudioMixer mixer;
    public AudioSource driver; // The driver is the conductor's source for musical time. Everything is relative to this.
    public AudioMixerSnapshot[] snapshots;
    public int[] segmentRepeats;
    public float[] transitionTimes;

    private float driverLastTime = -1.0f;
    private int currentSnapshot = 0;
    private int segmentCounter = 0;
    private IEnumerator transition;
    private bool isPaused = false;

    public void OnStateChange(string state)
    {

        if(state == "intro"){snapshots[0].TransitionTo(transitionTimes[0]);} // Transition to mixer snapshot
        else if(state == "v1"){snapshots[1].TransitionTo(transitionTimes[1]);}
        else if(state == "breakdown"){snapshots[2].TransitionTo(transitionTimes[2]);}
        else if(state == "pauseChange")
        {
            float targetValue;
            float startValue;
            // Puts value exposed mixer paramete into startValue.
            mixer.GetFloat("Lowpass", out startValue);
            float startTime = Time.time;

            // Flip the pause state i.e. if paused, resume.
            isPaused = !isPaused;

            if (transition != null)
            {
                // If the Coroutine is already running, stop it.

                // This needs to be here or the function can be fired mutiple times and if the direction needs to be flipped,
                // there won't be a battle between 2 Coroutines trying to simoltantiously lower and raise the value.
                StopCoroutine(transition);
            }

            if (isPaused)
            {
                // If we are paused.

                // Sets the target value for the effect if paused.
                targetValue = pauseFilterCutoff;

            }
            else
            {
                // Sets the target value for the effect if not pasued.
                // Probably should be using a mixer.get function to find the max value,
                // but I'm not sure if one exists.
                targetValue = 22000f;
            }
            // Setting coroutine to reference so it can be stopped with StopCoroutine() later.
            transition = TransitionEffect(mixer, "Lowpass", targetValue, startValue, pauseFilterCutoffDuration, startTime);
            // Adds coroutine to Unitys IEnumerators thing to run.
            StartCoroutine(transition);
        }
    }

    // Transitions mixer effect to specific vale over a period of time.
    private IEnumerator TransitionEffect(AudioMixer mixer, string effect, float targetValue, float startingValue, float duration, float startTime)
    {
        float targetTime = startTime+duration;
        float progress;
        float currentTime;
        float lerp;

        do
        {
            currentTime = Time.time;
            // Calculates how far along in the transition is (value bewteen 0f (0%) and 1f (100%).
            progress = (currentTime-startTime)/duration;

            // Performs a linear interpolation to calculate what the mixer parameter should be at this momeent in time.
            lerp = Mathf.Lerp(startingValue, targetValue, progress);

            // Sets mixer parameter to lerp calculation.
            // SetFloat() stops snap snots from being able to modify this value.
            mixer.SetFloat(effect, lerp);

            // Wait for some time to run again.
            // This stops the loop from running a bagillion times and eating up all the system resources.
            yield return new WaitForSeconds(0.05f);
        }while(currentTime <= targetTime);
    }

    // Update is called once per frame
    void Update()
    {
        if (driver.time < driverLastTime)
        {
            // If driver's current play time < the last checked play time (i.e. clip has looped).

            if (++segmentCounter == segmentRepeats[currentSnapshot])
            {
                segmentCounter = 0;
                currentSnapshot = (currentSnapshot + 1 ) % snapshots.Length;
                snapshots[currentSnapshot].TransitionTo(transitionTimes[currentSnapshot]);
            }
        }
        // Stores the current position of the driver's playhead.
        driverLastTime = driver.time;
    }
}
