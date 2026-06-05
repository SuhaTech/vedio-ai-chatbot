function Metric({ label, value }) {
  return (
    <div className="bg-slate-50 rounded-xl p-3 text-center">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <strong className="block mt-1 text-lg">
        {value ?? 'N/A'}
      </strong>
    </div>
  )
}

function VideoCard({ video }) {
  const thumbnail =
    video.thumbnail ||
    `https://picsum.photos/seed/${video.video_id}/400/240`

  return (
    <article className="bg-white rounded-2xl shadow-md hover:shadow-xl transition overflow-hidden">
      <img
        src={thumbnail}
        alt={video.creator}
        className="w-full h-52 object-cover"
      />

      <div className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-lg">
              {video.creator}
            </h3>

            <p className="text-sm text-slate-500">
              Video {video.video_id}
            </p>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              video.platform === 'youtube'
                ? 'bg-red-100 text-red-600'
                : 'bg-pink-100 text-pink-600'
            }`}
          >
            {video.platform}
          </span>
        </div>

        <p className="mt-4 text-sm text-slate-600 line-clamp-3">
          {video.transcript?.slice(0, 180)}
        </p>

        <div className="grid grid-cols-3 gap-3 mt-4">
          <Metric
            label="Views"
            value={video.views}
          />

          <Metric
            label="Likes"
            value={video.likes}
          />

          <Metric
            label="Comments"
            value={video.comments}
          />

          <Metric
            label="Followers"
            value={video.followers}
          />

          <Metric
            label="Duration"
            value={video.duration}
          />

          <Metric
            label="Upload"
            value={video.upload_date}
          />
        </div>

        <div className="mt-4 rounded-xl border border-green-200 bg-green-50 p-4">
          <p className="text-xs text-green-700">
            Engagement Rate
          </p>

          <h2 className="text-2xl font-bold text-green-700">
            {video.engagement_rate}%
          </h2>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {video.hashtags?.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-slate-100 px-2 py-1 text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </article>
  )
}

export default function VideoCards({
  videos
}) {
  return (
    <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
      {videos.map((video) => (
        <VideoCard
          key={video.video_id}
          video={video}
        />
      ))}
    </section>
  )
}