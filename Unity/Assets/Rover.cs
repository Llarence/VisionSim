using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class Rover : MonoBehaviour {
    // Rotations per second
    public float maxSpeed;
    public float steeringRange;

    public WheelCollider[] frontWheels;

    public float noiseRange;

    WheelCollider[] wheels;

#if !UNITY_EDITOR
    Connection connection;
#endif

    void Start() {
        wheels = GetComponentsInChildren<WheelCollider>();

#if !UNITY_EDITOR
        Application.targetFrameRate = 24;
        connection = new Connection("localhost", int.Parse(Environment.GetCommandLineArgs()[1]));
#endif
    }

    void Update() {
#if UNITY_EDITOR
        Move move = new Move(Input.GetAxisRaw("Vertical"), Input.GetAxisRaw("Horizontal"));
#else
        Move move = connection.get();
#endif

        foreach (WheelCollider wheel in wheels) {
            if (frontWheels.Contains(wheel)) {
                wheel.steerAngle = Mathf.Clamp(move.rotate, -1F, 1F) * steeringRange;
            }

            wheel.rotationSpeed = Mathf.Clamp(move.forward, -1F, 1F) * 360F * maxSpeed;
        }

#if !UNITY_EDITOR
        // Should add better noise
        connection.set(new Pose(new Vector2(transform.position.x, transform.position.z) + (UnityEngine.Random.insideUnitCircle * noiseRange), transform.rotation));
#endif
    }
}
