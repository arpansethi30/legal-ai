import Link from 'next/link';

const CTA = () => {
  return (
    <section className="py-16 md:py-24 px-6 md:px-12">
      <div className="max-w-5xl mx-auto bg-gradient-to-r from-blue-600 to-blue-800 dark:from-blue-700 dark:to-blue-900 rounded-2xl shadow-xl overflow-hidden">
        <div className="flex flex-col md:flex-row">
          <div className="p-8 md:p-12 md:w-2/3">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Transform Your Legal Workflow?
            </h2>
            <p className="text-blue-100 text-lg mb-8 max-w-xl">
              Join thousands of legal professionals who are saving time, reducing errors, 
              and delivering better results with LegalAI. Start your free trial today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                href="/signup" 
                className="px-6 py-3 rounded-lg bg-white text-blue-700 hover:bg-blue-50 transition-colors text-center font-medium shadow-md hover:shadow-lg"
              >
                Start Free Trial
              </Link>
              <Link 
                href="/demo" 
                className="px-6 py-3 rounded-lg bg-transparent border border-white text-white hover:bg-blue-700 transition-colors text-center font-medium"
              >
                Request Demo
              </Link>
            </div>
          </div>
          <div className="hidden md:block md:w-1/3 bg-blue-800 dark:bg-blue-900 relative">
            <div className="absolute inset-0 opacity-20">
              <svg className="h-full w-full" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
                <path fill="#fff" d="M37.5,186c-12.1-10.5-11.8-32.3-7.2-46.7c4.8-15,13.1-17.8,30.1-36.7C91,68.8,83.5,56.7,103.5,45 c22.2-13.1,51.1-9.5,69.6-1.6c18.1,7.8,15.7,15.3,43.3,33.2c28.8,18.8,37.2,14.3,46.7,27.9c15.6,22.3,6.4,53.3,4.4,60.2 c-3.3,11.2-7.1,23.9-18.5,32c-16.3,11.5-29.5,0.7-48.6,11c-16.2,8.7-12.6,19.7-28.2,33.2c-22.7,19.7-63.8,25.7-79.9,9.7 c-15.2-15.1,0.3-41.7-16.6-54.9C63,186,49.7,196.7,37.5,186z"></path>
              </svg>
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-white">
                <p className="text-5xl font-bold">14</p>
                <p className="text-xl">Day Free Trial</p>
                <p className="mt-4 text-sm text-blue-100">No credit card required</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA; 