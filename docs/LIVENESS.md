# Active challenge — experimental only

BioAuth requires a randomized **center → left/right → center** head-position challenge before comparing face embeddings. The command rejects static-image verification as an authentication path.

## Limitations
This is **not** reliable protection against presentation attacks. A moving printed photograph, prerecorded video, camera-feed injection, or a real-time deepfake may satisfy the challenge. Horizontal image position is not equivalent to measured head pose. An attacker could reposition a screen. No claims of certified PAD, ISO/IEC 30107 evaluation, or production security are made.

## Validation
Automated tests cover synthetic sequences, stationary images, wrong direction, and missing face. Real-camera tests against printed photos, screens, replay, and injection have NOT been completed. Keep PAM disabled and passwords enabled.
