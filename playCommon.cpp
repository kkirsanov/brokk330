#include <GL/GLee.h>
#include <GL/glut.h>
#include <pthread.h>
#include "Timer.h"

extern "C"{
#include "libavutil/avstring.h"
#include "libavformat/avformat.h"
#include "libavdevice/avdevice.h"
#include "libswscale/swscale.h"
#include "libavcodec/opt.h"
}

#include "playCommon.hh"
#include "BasicUsageEnvironment.hh"
#include "GroupsockHelper.hh"

#if !defined(__WIN32__) && !defined(_WIN32)
#include <signal.h>
#define USE_SIGNALS 1
#endif

#include <Python.h>

#define FPS 25.0f

#define TEX_SIZE 1024
bool use_pbo = 1;
bool use_recttex = 1;
int TEX_TYPE = GL_TEXTURE_RECTANGLE_ARB;

Timer t1, t2;
void *kkk(void* d);

typedef struct VIDEO
{
    AVCodecContext *pCodecCtx;
    AVCodec *pCodec;
    AVFrame *pFrame;
    int videoStream;
    
    AVPacket packet;
    int      bytesRemaining;
    uint8_t  *rawData;
    SwsContext *swsctx;
    
    int newf;
    int busy;
    
    RTSPClient* ourClient;
    MediaSession* session;
    
    bool saveToFile;
    bool rw;
    FILE *fh;
    
    char *headerData;
    int headerSize;

    int kk;
} VIDEO;

typedef struct VIEW
{
    int video;
    float x,y,w,h;
} VIEW;


// Forward function definitions:
int add_video(char *url);
void destroy_video(VIDEO *video);
void setupStreams(VIDEO* video);
void startPlayingStreams(VIDEO *video);
void tearDownStreams();
void closeMediaSinks();
void subsessionAfterPlaying(void* clientData);
void subsessionByeHandler(void* clientData);
void sessionAfterPlaying(void* clientData = NULL);
void shutdown(int exitCode = 1);
void signalHandlerShutdown(int sig);
void checkForPacketArrival(void* clientData);
void checkInterPacketGaps(void* clientData);

char const* progName;
UsageEnvironment* env;
TaskToken arrivalCheckTimerTask = NULL;
TaskToken interPacketGapCheckTimerTask = NULL;
char const* singleMedium = NULL;
int verbosityLevel = 1;
double duration = 0;
double durationSlop = 0.0; // extra seconds to play at the end
unsigned interPacketGapMaxTime = 0;
unsigned totNumPacketsReceived = ~0; // used if checking inter-packet gaps
Boolean playContinuously = False;
int simpleRTPoffsetArg = -1;
Boolean sendOptionsRequest = True;
Boolean oneFilePerFrame = False;
Boolean notifyOnPacketArrival = False;
Boolean streamUsingTCP = True;
char* username = NULL;
char* password = NULL;
char* proxyServerName = NULL;
unsigned short proxyServerPortNum = 0;
unsigned char desiredAudioRTPPayloadFormat = 0;
unsigned socketInputBufferSize = 0;
Boolean packetLossCompensate = False;
Boolean syncStreams = False;
Boolean generateHintTracks = False;

/*
    case 'D': { // specify maximum number of seconds to wait for packets:
      if (sscanf(argv[2], "%u", &interPacketGapMaxTime) != 1) {

    case 'c': { // play continuously
      playContinuously = True;

    case 'n': { // notify the user when the first data packet arrives
      notifyOnPacketArrival = True;
  */


struct timeval startTime;
GLuint tex[1000], glbuf[1000];

VIDEO videos[1000];
int numvideos = 0;
int curvideo = -1;

VIEW views[1000];
int numviews = 0;


class MySink: public MediaSink
{
public:
    MySink(UsageEnvironment& env, VIDEO *v);
    virtual ~MySink();

    void addData(unsigned char* data, unsigned dataSize, struct timeval presentationTime);

protected:
    static void afterGettingFrame(void* clientData, unsigned frameSize, unsigned numTruncatedBytes, struct timeval presentationTime, unsigned durationInMicroseconds);
    virtual void afterGettingFrame1(unsigned frameSize, struct timeval presentationTime);

    unsigned char* fBuffer;
    unsigned fBufferSize;
    VIDEO *video;

private:
    virtual Boolean continuePlaying();
};


MySink::MySink(UsageEnvironment& env, VIDEO *v): MediaSink(env)
{
    video = v;
    fBufferSize = 200000;
    fBuffer = new unsigned char[fBufferSize];
}

MySink::~MySink()
{
    delete[] fBuffer;
}

Boolean MySink::continuePlaying()
{
    if (fSource == NULL) return False;
    fSource->getNextFrame(fBuffer, fBufferSize, afterGettingFrame, this, onSourceClosure, this);

    return True;
}

void MySink::afterGettingFrame(void* clientData, unsigned frameSize, unsigned /*numTruncatedBytes*/, struct timeval presentationTime, unsigned /*durationInMicroseconds*/)
{
    MySink* sink = (MySink*)clientData;
    sink->afterGettingFrame1(frameSize, presentationTime);
}

void MySink::addData(unsigned char* data, unsigned dataSize, struct timeval presentationTime)
{
    int got_picture = 0;

    if (!video->headerData)
    {
        video->headerData = new char[dataSize];
        video->headerSize = dataSize;
        memcpy(video->headerData, data, dataSize);
    }

    if (video->saveToFile && video->rw)
        fwrite(data, 1, dataSize, video->fh);

    int br = dataSize;
    unsigned char *buf = data;
    int gp = 0;

    //while(video->busy);
    video->busy = 1;
    while (br > 0)
    {
        int len = avcodec_decode_video(video->pCodecCtx, video->pFrame, &got_picture, buf, br);
        
        br -= len;
        buf += len;
        if (got_picture)
        {
//            t1.stop();
//            printf ("%lf %lf ms\n", t2.getElapsedTimeInMilliSec(), t1.getElapsedTimeInMilliSec());
//            t1.start();
            video->newf = 1;
            if (video->saveToFile && !video->rw)
            {
                video->rw = true;
                fwrite(video->headerData, 1, video->headerSize, video->fh);
                fwrite(buf, 1, br, video->fh);
            }
        }
    }
    video->busy = 0;
}

void MySink::afterGettingFrame1(unsigned frameSize, struct timeval presentationTime)
{
  addData(fBuffer, frameSize, presentationTime);
  continuePlaying();
}

uint8_t bbb[TEX_SIZE*TEX_SIZE*4];
void update_video(int i)
{
    AVPicture pict;
    VIDEO *video = &videos[i];

    if (video->newf && use_pbo)
    {
        int cbi = i*2 + video->kk;
        video->kk = !video->kk;
        int nbi = i*2 + video->kk;

        //create buffers and textures
        if (!glbuf[cbi])
        {
            glGenBuffersARB(2, &glbuf[i*2]);
       
            glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, glbuf[i*2]);
            glBufferDataARB(GL_PIXEL_UNPACK_BUFFER_ARB, TEX_SIZE*TEX_SIZE*4, NULL, GL_DYNAMIC_DRAW_ARB);

            glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, glbuf[i*2+1]);
            glBufferDataARB(GL_PIXEL_UNPACK_BUFFER_ARB, TEX_SIZE*TEX_SIZE*4, NULL, GL_DYNAMIC_DRAW_ARB);
        }
        if (!tex[i])
        {
	        glGenTextures(1, &tex[i]);

          	glBindTexture(TEX_TYPE, tex[i]);
           	glTexParameteri(TEX_TYPE,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
           	glTexParameteri(TEX_TYPE,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
           	if (!use_recttex)
                glTexImage2D(TEX_TYPE, 0, 4, TEX_SIZE, TEX_SIZE, 0, GL_BGRA, GL_UNSIGNED_BYTE, 0);
        }

        //create texture for last frame
        glBindTexture(TEX_TYPE, tex[i]);
        glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, glbuf[cbi]);
        glTexImage2D(TEX_TYPE, 0, 4, TEX_SIZE, TEX_SIZE, 0, GL_BGRA, GL_UNSIGNED_BYTE, 0);

        //prepare buffer for current frame
        glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, glbuf[nbi]);

        pict.data[0] = (uint8_t*)glMapBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, GL_WRITE_ONLY_ARB);
        pict.linesize[0] = TEX_SIZE*4;

        if (!video->swsctx)
            video->swsctx = sws_getContext(video->pCodecCtx->width, video->pCodecCtx->height, video->pCodecCtx->pix_fmt, video->pCodecCtx->width, video->pCodecCtx->height, PIX_FMT_RGB32, SWS_BICUBIC, NULL, NULL, NULL);

        //while(video->busy);
        video->busy = 1;
        sws_scale(video->swsctx, video->pFrame->data, video->pFrame->linesize, 0, video->pCodecCtx->height, pict.data, pict.linesize);
        video->busy = 0;

        glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER_ARB);
        //glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, 0);
    }
    
    if (video->newf && !use_pbo)
    {
        video->newf = 0;   
        pict.data[0] = bbb;
        pict.linesize[0] = video->pCodecCtx->width*4;

        if (!video->swsctx)
            video->swsctx = sws_getContext(video->pCodecCtx->width, video->pCodecCtx->height, video->pCodecCtx->pix_fmt, video->pCodecCtx->width, video->pCodecCtx->height, PIX_FMT_BGR32, SWS_BICUBIC, NULL, NULL, NULL);

        while (video->busy);
        video->busy = 1;
        sws_scale(video->swsctx, video->pFrame->data, video->pFrame->linesize, 0, video->pCodecCtx->height, pict.data, pict.linesize);
        video->busy = 0;

        glBindTexture(TEX_TYPE, tex[i]);
        
        if (use_recttex)
           glTexImage2D(TEX_TYPE, 0, 4, video->pCodecCtx->width, video->pCodecCtx->height, 0, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, bbb);
        else
           glTexSubImage2D(TEX_TYPE, 0, 0, 0, video->pCodecCtx->width, video->pCodecCtx->height, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, bbb);
    }
}


void display_video(int i, float x, float y, float w, float h)
{
    VIDEO *video = &videos[i];
    
    glBindTexture(TEX_TYPE, tex[i]);
    
    glPushMatrix();
    
    glTranslatef(x, y, 0);

    if (use_recttex)
    {        
        glBegin(GL_QUADS);    
            glTexCoord2f(0,0);
            glVertex2f(0, 0);
    
            glTexCoord2f(0, video->pCodecCtx->height);
            glVertex2f(0, h);
    
            glTexCoord2f(video->pCodecCtx->width, video->pCodecCtx->height);
            glVertex2f(w, h);
    
            glTexCoord2f(video->pCodecCtx->width,0);
            glVertex2f(w, 0);
        glEnd();
    }
    else
    {
        glBegin(GL_QUADS);    
            glTexCoord2f(0,0);
            glVertex2f(0, 0);
    
            glTexCoord2f(0, 1.0/TEX_SIZE*video->pCodecCtx->height);
            glVertex2f(0, h);
    
            glTexCoord2f(1.0/TEX_SIZE*video->pCodecCtx->width, 1.0/TEX_SIZE*video->pCodecCtx->height);
            glVertex2f(w, h);
    
            glTexCoord2f(1.0/TEX_SIZE*video->pCodecCtx->width,0);
            glVertex2f(w, 0);
        glEnd();
    }
    
    if (video->saveToFile)
    {
        glDisable(TEX_TYPE);
        glColor4f(1.0f, 0.0f, 0.0f,1 );
        
        glBegin(GL_QUADS);    
            glVertex2f(0, 0);
            glVertex2f(0, 10);
            glVertex2f(10, 10);
            glVertex2f(10, 0);
        glEnd();

        glEnable(TEX_TYPE);
        glColor4f(1.0f, 1.0f, 1.0f,1 );
    }
    
    glPopMatrix();
}


static void display(void)
{
    for (int i = 0; i < numvideos; i++)
        update_video(i);

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glColor4f(1.0f, 1.0f, 1.0f,1 );

    for (int i = 0; i < numviews; i++)
    {
    	VIEW *v = &views[i];
    	display_video(v->video, v->x,v->y,v->w,v->h);
    }

    glBindBufferARB(GL_PIXEL_UNPACK_BUFFER_ARB, 0);
    glutSwapBuffers();
}


static void resize(int width, int height)
{
    glViewport(0, 0, width, height);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0,width,height,0,0,100);
    
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity() ;
}

static void timer(int a)
{
    glutPostRedisplay();
    glutTimerFunc(1000.0f/FPS, timer, 0);
}

static void key(unsigned char key, int x, int y)
{
    switch (key) 
    {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
            if (key - '0' - 1 >= numvideos)
                break;
            curvideo = key - '0' - 1;
            break;
        
        case 27 : 
        case 'q':
            exit(0);
            break;
    }
}



void initGL()
{
    t2.start();
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH);
    glutCreateWindow("BROK 330");
    glutReshapeFunc(resize);
    glutDisplayFunc(display);
    glutKeyboardFunc(key);
    glClearColor(0, 0, 0, 1);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4);

    if (!GLEE_ARB_pixel_buffer_object)
        use_pbo = false;
    if (!GLEE_ARB_texture_rectangle)
        use_recttex = false;

    if (use_pbo)
        use_recttex = false;
    else
        glPixelStorei(GL_UNPACK_CLIENT_STORAGE_APPLE, GL_TRUE);

    if (!use_recttex)
       TEX_TYPE = GL_TEXTURE_2D;
    
    glEnable(TEX_TYPE);

    printf ("GL: TEXTURE_RECTANGLE = %d, PBO = %d\n", use_recttex, use_pbo);
}

void *ttt(void* d)
{
    while(1) ((BasicTaskScheduler0*)&env->taskScheduler())->SingleStep(0.5*1000*1000);
    pthread_exit(NULL);
}


void init_video(VIDEO *video)
{
    bzero (video, sizeof(VIDEO));
    video->pCodecCtx = avcodec_alloc_context();         
    AVCodec *codec = avcodec_find_decoder(CODEC_ID_MPEG4);
    if (!codec)
    {
        printf("no codec!\n");
        exit(0);
    }
    video->pCodec = codec;
    if(video->pCodec->capabilities & CODEC_CAP_TRUNCATED)
        video->pCodecCtx->flags|=CODEC_FLAG_TRUNCATED;
    if(avcodec_open(video->pCodecCtx, video->pCodec)<0)
    {
        printf("can't open codec\n");
        exit(0);         
    }

    video->pFrame = avcodec_alloc_frame();
}

int open_stream(char *url, VIDEO *video)
{
    unsigned short desiredPortNum = 0;
    
    // Create our client object:
    video->ourClient = RTSPClient::createNew(*env, verbosityLevel, "prj4", 0);
    if (video->ourClient == NULL)
    {
        *env << "Failed to create RTSP client: " << env->getResultMsg() << "\n";
        return 0;
    }

    if (sendOptionsRequest)
    {
        char* optionsResponse = video->ourClient->sendOptionsCmd(url, username, password);
        delete[] optionsResponse;
    }

    //Open the URL to get a SDP description
    char* sdpDescription;        
    if (username != NULL && password != NULL)
        sdpDescription = video->ourClient->describeWithPassword(url, username, password);
    else
        sdpDescription = video->ourClient->describeURL(url);
                
    if (sdpDescription == NULL)
    {
        *env << "Failed to get a SDP description from URL \"" << url << "\": " << env->getResultMsg() << "\n";
        return 0;
    }
    *env << "Opened URL \"" << url << "\n";

    //Create a media session object from this SDP description:
    video->session = MediaSession::createNew(*env, sdpDescription);
    delete[] sdpDescription;
    
    if (video->session == NULL)
    {
        *env << "Failed to create a MediaSession object from the SDP description: " << env->getResultMsg() << "\n";
        return 0;
    }
    
    if (!video->session->hasSubsessions())
    {
        *env << "This session has no media subsessions (i.e., \"m=\" lines)\n";
        return 0;
    }

    //Setup the "RTPSource"s for the session:
    MediaSubsessionIterator iter(*video->session);
    MediaSubsession *subsession;
    Boolean madeProgress = False;
  
    while ((subsession = iter.next()) != NULL)
    {
        if (strcmp(subsession->mediumName(), "video") != 0)
            continue;
        
        if (desiredPortNum != 0)
        {
            subsession->setClientPortNum(desiredPortNum);
            desiredPortNum += 2;
        }

        if (!subsession->initiate(simpleRTPoffsetArg))
		    *env << "Unable to create receiver for \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession: " << env->getResultMsg() << "\n";
        else
        {
		    *env << "Created receiver for \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession (client ports " << subsession->clientPortNum() << "-" << subsession->clientPortNum()+1 << ")\n";
		    madeProgress = True;

		    if (subsession->rtpSource() != NULL)
            {
                // Because we're saving the incoming data, rather than playing
                // it in real time, allow an especially large time threshold
                // (1 second) for reordering misordered incoming packets:
                unsigned const thresh = 500000; //0.5sec
                subsession->rtpSource()->setPacketReorderingThresholdTime(thresh);

                if (socketInputBufferSize > 0)
                {
                    // Set the RTP source's input buffer size as specified:
                    int socketNum = subsession->rtpSource()->RTPgs()->socketNum();

                    unsigned curBufferSize = getReceiveBufferSize(*env, socketNum);
                    unsigned newBufferSize = setReceiveBufferTo(*env, socketNum, socketInputBufferSize);
                    *env << "Changed socket receive buffer size for the \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession from " << curBufferSize << " to " << newBufferSize << " bytes\n";
                }
            }
        }
      
        break; //process only one (first) video subsession
    }
    if (!madeProgress) return 0;

    //Perform additional 'setup' on each subsession, before playing them:
    setupStreams(video);

    {
        madeProgress = False;
        iter.reset();
        while ((subsession = iter.next()) != NULL)
        {
            if (subsession->readSource() == NULL) continue; // was not initiated

            subsession->sink = new MySink(*env, video);

	        if (subsession->sink != NULL)
            {
	            if (strcmp(subsession->mediumName(), "video") == 0 && strcmp(subsession->codecName(), "MP4V-ES") == 0 && subsession->fmtp_config() != NULL)
                {
	                // For MPEG-4 video RTP streams, the 'config' information
	                // from the SDP description contains useful VOL etc. headers.
	                // Insert this data at the front of the output file:
	                unsigned configLen;
	                unsigned char* configData = parseGeneralConfigStr(subsession->fmtp_config(), configLen);
	                struct timeval timeNow;
	                gettimeofday(&timeNow, NULL);
	                ((MySink*)subsession->sink)->addData(configData, configLen, timeNow);
	                printf ("------ %d\n", configLen);
	                delete[] configData;
                }

                subsession->sink->startPlaying(*(subsession->readSource()), subsessionAfterPlaying, subsession);

                // Also set a handler to be called if a RTCP "BYE" arrives
                // for this subsession:
                if (subsession->rtcpInstance() != NULL)
                    subsession->rtcpInstance()->setByeHandler(subsessionByeHandler, subsession);

                madeProgress = True;
            }
        }
    
        if (!madeProgress) return 0;
    }

    return 1;
}

int add_video(char *url)
{
    init_video(&videos[numvideos]);
    if (open_stream(url, &videos[numvideos]))
    {
        startPlayingStreams(&videos[numvideos]);

        numvideos++;
        return 1;
    }
    
    destroy_video(&videos[numvideos]);
    return 0;
}

void destroy_video(VIDEO *video)
{
    if (video)
    {
        if (video->ourClient)
        {
            if (video->session)
            {
                video->ourClient->teardownMediaSession(*video->session);
            }

            //delete video->ourClient;
        }
    }
}

int main(int argc, char** argv)
{
    TaskScheduler* scheduler = BasicTaskScheduler::createNew();
    env = BasicUsageEnvironment::createNew(*scheduler);
    gettimeofday(&startTime, NULL);
  
#ifdef USE_SIGNALS
    signal(SIGHUP, signalHandlerShutdown);
    signal(SIGUSR1, signalHandlerShutdown);
#endif

    av_register_all();         
  
    glutInit(&argc, argv);
    glutInitWindowPosition(10,10);
    glutInitWindowSize(1000, 700);

    initGL();

    glutTimerFunc(1000.0f/FPS, timer, 0);
  
    int prio;
    pthread_t tid, kid;
    pthread_attr_t attr;
    struct sched_param sched;

    pthread_attr_init (&attr);
    pthread_attr_getschedpolicy(&attr, &prio);
    pthread_attr_getschedparam (&attr, &sched);
    sched.sched_priority = prio;
    pthread_attr_setschedparam (&attr, &sched);

    pthread_create(&tid, NULL, &ttt, NULL); //stream receiver
    pthread_create(&kid, NULL, &kkk, NULL); //python interpreter
  
    glutMainLoop();

    return 0;
}

void setupStreams(VIDEO *video)
{
  MediaSubsessionIterator iter(*video->session);
  MediaSubsession *subsession;
  Boolean madeProgress = False;

  while ((subsession = iter.next()) != NULL) {
    if (subsession->clientPortNum() == 0) continue; // port # was not set

    if (!video->ourClient->setupMediaSubsession(*subsession, False, streamUsingTCP)) {
      *env << "Failed to setup \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession: " << env->getResultMsg() << "\n";
    } else {
      *env << "Setup \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession (client ports " << subsession->clientPortNum() << "-" << subsession->clientPortNum()+1 << ")\n";
      madeProgress = True;
    }
  }
  if (!madeProgress) shutdown();
}

void startPlayingStreams(VIDEO *video)
{
    duration = video->session->playEndTime();

    if (!video->ourClient->playMediaSession(*video->session, 0,0, 1))
    {
        *env << "Failed to start playing session: " << env->getResultMsg() << "\n";
        shutdown();
    }
    else
        *env << "Started playing session\n";

    char const* actionString = "Receiving streamed data";
}

void closeMediaSinks()
{
    if (videos[0].session == NULL) return;
    MediaSubsessionIterator iter(*videos[0].session);
    MediaSubsession* subsession;
    while ((subsession = iter.next()) != NULL)
    {
        Medium::close(subsession->sink);
        subsession->sink = NULL;
    }
}

void subsessionAfterPlaying(void* clientData) {
    //Begin by closing this media subsession's stream
    MediaSubsession* subsession = (MediaSubsession*)clientData;
    Medium::close(subsession->sink);
    subsession->sink = NULL;

    //Next, check whether *all* subsessions' streams have now been closed
    MediaSession& session = subsession->parentSession();
    MediaSubsessionIterator iter(session);
    while ((subsession = iter.next()) != NULL)
        if (subsession->sink != NULL) return; //this subsession is still active

    //All subsessions' streams have now been closed
    sessionAfterPlaying();
}

void subsessionByeHandler(void* clientData)
{
    struct timeval timeNow;
    gettimeofday(&timeNow, NULL);
    unsigned secsDiff = timeNow.tv_sec - startTime.tv_sec;

    MediaSubsession* subsession = (MediaSubsession*)clientData;
    *env << "Received RTCP \"BYE\" on \"" << subsession->mediumName() << "/" << subsession->codecName() << "\" subsession (after " << secsDiff << " seconds)\n";

    //Act now as if the subsession had closed
    subsessionAfterPlaying(subsession);
}

void sessionAfterPlaying(void* /*clientData*/)
{
}

void shutdown(int exitCode)
{
    if (env != NULL)
    {
        env->taskScheduler().unscheduleDelayedTask(arrivalCheckTimerTask);
        env->taskScheduler().unscheduleDelayedTask(interPacketGapCheckTimerTask);
    }

    //closeMediaSinks();

    exit(exitCode);
}

void signalHandlerShutdown(int /*sig*/)
{
    *env << "Got shutdown signal\n";
    shutdown(0);
}

void checkInterPacketGaps(void* /*clientData*/)
{
    if (interPacketGapMaxTime == 0) return; //we're not checking

    //Check each subsession, counting up how many packets have been received:
    unsigned newTotNumPacketsReceived = 0;

    MediaSubsessionIterator iter(*videos[0].session);
    MediaSubsession* subsession;
    while ((subsession = iter.next()) != NULL)
    {
        RTPSource* src = subsession->rtpSource();
        if (src == NULL) continue;
        newTotNumPacketsReceived += src->receptionStatsDB().totNumPacketsReceived();
    }

    if (newTotNumPacketsReceived == totNumPacketsReceived)
    {
        //No additional packets have been received since the last time we
        //checked, so end this stream:
        *env << "Closing session, because we stopped receiving packets.\n";
        interPacketGapCheckTimerTask = NULL;
        sessionAfterPlaying();
    }
    else
    {
        totNumPacketsReceived = newTotNumPacketsReceived;
        //Check again, after the specified delay:
        interPacketGapCheckTimerTask = env->taskScheduler().scheduleDelayedTask(interPacketGapMaxTime*1000000, (TaskFunc*)checkInterPacketGaps, NULL);
    }
}





static PyObject* emb_addStream(PyObject *self, PyObject *args)
{
    char *url;
    if (PyArg_ParseTuple(args, "s", &url))
    {
        printf ("addVideo: %s\n", url);
        if (!add_video(url))
	        return Py_BuildValue("i", 0);
        return Py_BuildValue("i", numvideos);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* emb_addView(PyObject *self, PyObject *args)
{
    int video;
    float x,y,w,h;

    if (PyArg_ParseTuple(args, "iffff", &video, &x,&y,&w,&h))
    {
        printf ("addView: %d %f %f %f %f\n", video, x,y,w,h);

        VIEW *v = &views[numviews];
        v->video = video-1;
        v->x = x;
        v->y = y;
        v->w = w;
        v->h = h;
        numviews++;

        return Py_BuildValue("i", numviews);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* emb_moveView(PyObject *self, PyObject *args)
{
    int view;
    float x,y,w,h;

    if (PyArg_ParseTuple(args, "iffff", &view, &x,&y,&w,&h))
    {
        printf ("moveView: %d %f %f %f %f\n", view, x,y,w,h);

        VIEW *v = &views[view-1];
        v->x = x;
        v->y = y;
        v->w = w;
        v->h = h;
        
        return Py_BuildValue("i", 1);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* emb_recordStart(PyObject *self, PyObject *args)
{
    int video;
    char *fn;

    if (PyArg_ParseTuple(args, "is", &video, &fn))
    {
        printf ("recordStart: %d %s\n", video, fn);

        VIDEO *v = &videos[video-1];
        if (!v->saveToFile)
        {
            v->fh = fopen(fn, "w+b");
            v->rw = false;
            v->saveToFile = true;
        }
        return Py_BuildValue("i", 1);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* emb_recordStop(PyObject *self, PyObject *args)
{
    int video;

    if (PyArg_ParseTuple(args, "i", &video))
    {
        printf ("recordStop: %d\n", video);

        VIDEO *v = &videos[video-1];
        if (v->saveToFile)
        {
            v->saveToFile = false;
            fclose(v->fh);
        }
        return Py_BuildValue("i", 1);
    }

    return Py_BuildValue("i", 0);
}

static PyObject* emb_moveWindow(PyObject *self, PyObject *args)
{
    float x,y,w,h;

    if (PyArg_ParseTuple(args, "ffff", &x,&y,&w,&h))
    {
        printf ("moveWindow: %f %f %f %f\n", x,y,w,h);

        glutPositionWindow(x,y);
        glutReshapeWindow(w,h);
        
        return Py_BuildValue("i", 1);
    }

    return Py_BuildValue("i", 0);
}
                
static PyMethodDef EmbMethods[] =
{
    {"addStream", emb_addStream, METH_VARARGS, ""},
    {"addView",  emb_addView, METH_VARARGS, ""},
    {"moveView",  emb_moveView, METH_VARARGS, ""},
    {"recordStart",  emb_recordStart, METH_VARARGS, ""},
    {"recordStop",  emb_recordStop, METH_VARARGS, ""},
    {"moveWindow", emb_moveWindow, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

void *kkk(void* d)
{
    Py_Initialize();
    Py_InitModule("emb", EmbMethods);

    FILE *fh = fopen("script.py", "r");
    PyRun_SimpleFile(fh, "script.py");
    
    Py_Finalize();
    pthread_exit(NULL);
}
                             
