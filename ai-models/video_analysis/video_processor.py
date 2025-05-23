# video_processor.py - Video processing and chunking module
import ffmpeg
import cv2
import numpy as np
import os
from typing import List, Dict, Tuple
import av
from pathlib import Path
import tempfile
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.chunk_duration = 30  # seconds
        self.overlap_duration = 5  # seconds
        self.frame_sample_rate = 3  # process every nth frame
        self.target_fps = 1  # frames per second for analysis
        
    def get_video_info(self, file_path: str) -> Dict:
        """Get basic video information using ffmpeg-python"""
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            info = {
                'duration': float(video_stream.get('duration', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                'has_audio': audio_stream is not None,
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate': int(video_stream.get('bit_rate', 0)) if video_stream.get('bit_rate') else None
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise
    
    def chunk_video(self, file_path: str, output_dir: str = None) -> List[str]:
        """Split video into overlapping chunks for processing"""
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            
            video_info = self.get_video_info(file_path)
            duration = video_info['duration']
            
            chunks = []
            start_time = 0
            chunk_index = 0
            
            while start_time < duration:
                chunk_filename = f"chunk_{chunk_index:04d}.mp4"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                # Calculate end time
                end_time = min(start_time + self.chunk_duration, duration)
                
                # Use ffmpeg to extract chunk
                (
                    ffmpeg
                    .input(file_path, ss=start_time, t=end_time - start_time)
                    .output(chunk_path, vcodec='libx264', acodec='aac')
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                chunks.append({
                    'path': chunk_path,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'index': chunk_index
                })
                
                # Move to next chunk with overlap consideration
                start_time += self.chunk_duration - self.overlap_duration
                chunk_index += 1
            
            logger.info(f"Created {len(chunks)} chunks from video")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking video: {e}")
            raise
    
    def extract_frames(self, chunk_info: Dict, smart_sampling: bool = True) -> List[Dict]:
        """Extract frames from video chunk with intelligent sampling"""
        try:
            chunk_path = chunk_info['path']
            start_time = chunk_info['start_time']
            
            frames = []
            
            # Open video with PyAV for more control
            container = av.open(chunk_path)
            video_stream = container.streams.video[0]
            
            frame_count = 0
            last_frame = None
            scene_change_threshold = 0.3  # Threshold for detecting scene changes
            
            for frame in container.decode(video=0):
                timestamp = float(frame.time)
                global_timestamp = start_time + timestamp
                
                # Convert frame to numpy array
                frame_array = frame.to_ndarray(format='rgb24')
                
                # Decide whether to include this frame
                include_frame = False
                
                if smart_sampling:
                    # Always include first frame
                    if frame_count == 0:
                        include_frame = True
                    else:
                        # Check for scene changes
                        if last_frame is not None:
                            # Simple scene change detection using histogram comparison
                            hist_diff = self._calculate_histogram_difference(frame_array, last_frame)
                            if hist_diff > scene_change_threshold:
                                include_frame = True
                        
                        # Regular sampling fallback
                        if not include_frame and frame_count % self.frame_sample_rate == 0:
                            include_frame = True
                else:
                    # Simple regular sampling
                    if frame_count % self.frame_sample_rate == 0:
                        include_frame = True
                
                if include_frame:
                    frames.append({
                        'frame_data': frame_array,
                        'timestamp': global_timestamp,
                        'frame_index': frame_count,
                        'chunk_timestamp': timestamp,
                        'width': frame_array.shape[1],
                        'height': frame_array.shape[0]
                    })
                    last_frame = frame_array.copy()
                
                frame_count += 1
            
            container.close()
            logger.info(f"Extracted {len(frames)} frames from chunk")
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            raise
    
    def _calculate_histogram_difference(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate histogram difference between two frames for scene change detection"""
        try:
            # Convert to grayscale for histogram comparison
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            
            # Calculate histograms
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
            
            # Calculate correlation coefficient
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Return difference (1 - correlation)
            return 1 - correlation
            
        except Exception as e:
            logger.error(f"Error calculating histogram difference: {e}")
            return 0
    
    def extract_audio(self, file_path: str, output_path: str = None) -> str:
        """Extract audio from video file"""
        try:
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.wav')
            
            # Extract audio using ffmpeg
            (
                ffmpeg
                .input(file_path)
                .output(output_path, acodec='pcm_s16le', ac=1, ar='16000')  # Mono, 16kHz for Whisper
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.info(f"Extracted audio to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def synchronize_videos(self, video_paths: List[str], output_dir: str = None) -> List[str]:
        """Synchronize multiple video files based on audio correlation"""
        try:
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            
            if len(video_paths) < 2:
                return video_paths
            
            # Extract audio from all videos
            audio_files = []
            for i, video_path in enumerate(video_paths):
                audio_path = os.path.join(output_dir, f"audio_{i}.wav")
                self.extract_audio(video_path, audio_path)
                audio_files.append(audio_path)
            
            # Find time offsets using cross-correlation
            offsets = self._calculate_audio_offsets(audio_files)
            
            # Create synchronized video files
            synchronized_paths = []
            for i, (video_path, offset) in enumerate(zip(video_paths, offsets)):
                sync_path = os.path.join(output_dir, f"sync_{i}_{Path(video_path).name}")
                
                if abs(offset) > 0.1:  # Only re-encode if significant offset
                    input_stream = ffmpeg.input(video_path)
                    if offset > 0:
                        # Delay video
                        input_stream = ffmpeg.filter(input_stream, 'adelay', f'{int(offset * 1000)}')
                    else:
                        # Trim video
                        input_stream = ffmpeg.input(video_path, ss=abs(offset))
                    
                    (
                        input_stream
                        .output(sync_path)
                        .overwrite_output()
                        .run(quiet=True)
                    )
                else:
                    # No sync needed, just copy
                    sync_path = video_path
                
                synchronized_paths.append(sync_path)
            
            logger.info(f"Synchronized {len(video_paths)} videos")
            return synchronized_paths
            
        except Exception as e:
            logger.error(f"Error synchronizing videos: {e}")
            raise
    
    def _calculate_audio_offsets(self, audio_files: List[str]) -> List[float]:
        """Calculate time offsets between audio files using cross-correlation"""
        try:
            # This is a simplified implementation
            # In production, you'd want more sophisticated audio alignment
            offsets = [0.0]  # First file is reference
            
            # Load reference audio
            import librosa
            ref_audio, sr = librosa.load(audio_files[0], sr=16000)
            
            for audio_file in audio_files[1:]:
                # Load comparison audio
                comp_audio, _ = librosa.load(audio_file, sr=16000)
                
                # Find offset using cross-correlation
                correlation = np.correlate(ref_audio, comp_audio, mode='full')
                offset_samples = np.argmax(correlation) - len(comp_audio) + 1
                offset_seconds = offset_samples / sr
                
                offsets.append(offset_seconds)
            
            return offsets
            
        except Exception as e:
            logger.error(f"Error calculating audio offsets: {e}")
            # Return zero offsets if calculation fails
            return [0.0] * len(audio_files)
    
    def resize_frame_for_analysis(self, frame: np.ndarray, max_size: int = 768) -> np.ndarray:
        """Resize frame while maintaining aspect ratio for efficient AI analysis"""
        try:
            height, width = frame.shape[:2]
            
            # Calculate new dimensions
            if width > height:
                new_width = min(width, max_size)
                new_height = int(height * (new_width / width))
            else:
                new_height = min(height, max_size)
                new_width = int(width * (new_height / height))
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized_frame
            
        except Exception as e:
            logger.error(f"Error resizing frame: {e}")
            return frame
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {file_path}: {e}")