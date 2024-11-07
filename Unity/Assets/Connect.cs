using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using UnityEngine;

public struct Move {
    public float forward;
    public float rotate;

    public Move(float forward, float rotate) {
        this.forward = forward;
        this.rotate = rotate;
    }
}

public struct Pose {
    public float[] buffer;

    public Pose(Vector2 pos, Quaternion rot) {
        buffer = new float[] {pos.x, pos.y, rot.eulerAngles.x, rot.eulerAngles.y, rot.eulerAngles.z};
    }
}

public class Connection : IDisposable {
    Socket socket;
    NetworkStream stream;

    Move move;

    public Connection(string host, int port) {
        socket = new Socket(SocketType.Stream, ProtocolType.Tcp);
        socket.Connect(host, port);

        stream = new NetworkStream(socket);

        move = new Move(1, 1);
    }

    public Move get() {
        int size = socket.Available - (socket.Available % 8);
        if (size > 0) {
            byte[] buffer = new byte[size];
            socket.Receive(buffer);

            float[] decoded = new float[2];
            Buffer.BlockCopy(buffer, size - 8, decoded, 0, 8);

            move = new Move(decoded[0], decoded[1]);
        }

        return move;
    }

    public void set(Pose pose) {
        byte[] buffer = new byte[20];
        Buffer.BlockCopy(pose.buffer, 0, buffer, 0, buffer.Length);

        socket.Send(buffer);
    }

    public void Dispose() {
        stream.Dispose();
        socket.Dispose();
    }
}
