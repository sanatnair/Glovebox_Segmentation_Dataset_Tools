## Video Folder Organization

Ensure that this folder is organized consistent with the glovebox segmentation dataset. This is important so the frame extraction script can easily locate and process the files based on the respective participant, view, and distribution type.

### Example

Organization should be similar to what is outlined as follows:

```
videos/
├── Test_Subject_1/
│   ├── Side_View/
│   │   ├── J_NG.mp4
│   │   ├── TB_GL.mp4
│   │   └── ...
│   ├── Top_View/
│   │   ├── J_GL.mp4
│   │   ├── TB_NG.mp4
│   │   └── ...
│
├── Test_Subject_2/
│   ├── Side_View/
│   │   ├── J_NG_G.mp4
│   │   ├── TB_GL.mp4
│   │   ├── TB_GL_G.mp4
│   │   └── ...
│   ├── Top_View/
│   │   ├── J_NG_G.mp4
│   │   ├── TB_GL.mp4
│   │   └── ...
│
├── Test_Subject_3/
│   ├── ...
│
└── ...
```

_In this example you have a `videos` directory as the root folder. Within the videos directory, there are subdirectories named `Test_Subject_1`, `Test_Subject_2`, and so on, each representing a different participant. Inside each participant's directory, you have two subdirectories: `Side_View` and `Top_View`, representing the two different camera views. Inside the `Side_View` and `Top_View` directories, you have video files with names like `J_NG.mp4`, `TB_GL.mp4`, and so on, which correspond to the specific video files for that participant and experiment. This should ultimately be consistent with the glovebox segmentation dataset_
