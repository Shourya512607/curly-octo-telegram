using VideoIO, Images, ImageView

try
    # Try to open default webcam (index 0)
    cam = try
        VideoIO.opencamera(0)
    catch e
        error("❌ Could not open webcam (device index 0). Check if a camera is connected.\n$(e)")
    end

    # Try reading a frame
    frame = try
        read(cam)
    catch e
        error("❌ Failed to read a frame from the webcam.\n$(e)")
    end

    if frame === nothing
        error("❌ Webcam returned nothing. Possible driver or device issue.")
    end

    println("✅ Webcam initialized successfully. Showing preview...")

    # Show a few frames
    for i in 1:50
        frame = read(cam)
        if frame === nothing
            error("❌ Webcam stopped producing frames unexpectedly.")
        end
        ImageView.imshow(frame)
    end

    close(cam)

catch e
    # Any unexpected errors will be caught here
    error("❌ Webcam test failed: $(e)")
end
